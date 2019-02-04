import json
import flask
from flask_cors import (
    cross_origin
)
from flask import (
    Flask,
    request
)
import logging
from http.client import responses
from flask.logging import default_handler
from .external_api.auth import (
    get_auth_token,
    validate_service_token,
    validate_user_token,
    is_feeds_admin
)
from .util import epoch_ms
from .config import get_config
from .exceptions import (
    MissingTokenError,
    InvalidTokenError,
    TokenLookupError,
    IllegalParameterError,
    MissingParameterError,
    NotificationNotFoundError
)
from feeds.api.api_v1 import api_v1
from feeds.api.admin_v1 import admin_v1
from feeds.logger import (
    log,
    log_error
)

VERSION = "0.2.0"

try:
    from feeds import gitcommit
except ImportError:  # pragma: no cover
    # tested manually
    raise ValueError('Did not find git commit file at feeds/gitcommit.py '   # pragma: no cover
                     'The build may not have completed correctly.')          # pragma: no cover


def _initialize_logging():
    root = logging.getLogger()
    root.addHandler(default_handler)
    root.setLevel('INFO')


def _log(msg, *args, level=logging.INFO):
    log(__name__, msg, *args, level=level)


def _log_error(error):
    log_error(__name__, error)


def _make_error(error, msg, status_code):
    _log("%s %s", status_code, msg)
    err_response = {
        "http_code": status_code,
        "http_status": responses[status_code],
        "message": msg,
        "time": epoch_ms()
    }
    return (flask.jsonify({'error': err_response}), status_code)


def create_app(test_config=None):
    _initialize_logging()
    cfg = get_config()

    app = Flask(__name__, instance_relative_config=True)
    app.config['DEBUG'] = cfg.debug
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.url_map.strict_slashes = False
    app.register_blueprint(api_v1, url_prefix='/api/V1')
    app.register_blueprint(admin_v1, url_prefix='/admin/api/V1')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.before_request
    def preprocess_request():
        _log('%s %s', request.method, request.path)
        pass

    @app.after_request
    def postprocess_request(response):
        _log('%s %s %s %s', request.method, request.path, response.status_code,
             request.headers.get('User-Agent'))
        return response

    @app.route('/', methods=['GET'])
    @cross_origin()
    def root():
        return flask.jsonify({
            "service": "Notification Feeds Service",
            "gitcommithash": gitcommit.commit,
            "version": VERSION,
            "servertime": epoch_ms()
        })

    @app.route('/permissions', methods=['GET'])
    @cross_origin()
    def permissions():
        """
        Returns permissions based on the token.
        """
        # default permissions without a token
        perms = {
            'token': {
                'user': None,
                'service': None,
                'admin': False
            },
            'permissions': {
                'POST': [],
                'GET': ['/api/V1/notifications/global']
            }
        }
        token = get_auth_token(request, required=False)
        if token is not None:
            try:
                user = validate_user_token(token)
                if user is not None:
                    perms['token']['user'] = user
                    perms['permissions']['GET'] = perms['permissions']['GET'] + \
                        ['/api/V1/notifications', '/api/V1/notification/<note_id>']
                    perms['permissions']['POST'] = perms['permissions']['POST'] + \
                        ['/api/V1/notifications/see', '/api/V1/notifications/unsee']
            except InvalidTokenError:
                pass
            try:
                service = validate_service_token(token)
                # TODO - add filter so only specific services can see these
                perms['token']['service'] = service
                perms['permissions']['GET'].append('/api/V1/notification/external_key/<key>')
                perms['permissions']['POST'] = perms['permissions']['POST'] + \
                    ['/api/V1/notification', '/api/V1/notifications/expire']
            except InvalidTokenError:
                pass
            if is_feeds_admin(token):
                perms['token']['admin'] = True
                perms['permissions']['POST'] = perms['permissions']['POST'] + \
                    ['/admin/api/V1/notification/global', '/admin/api/V1/notifications/expire']
        return (flask.jsonify(perms), 200)

    @app.errorhandler(IllegalParameterError)
    @app.errorhandler(json.JSONDecodeError)
    def handle_illegal_parameter(err):
        _log_error(err)
        msg = "Incorrect data format"
        if str(err):
            msg = str(err)
        return _make_error(err, msg, 400)

    @app.errorhandler(MissingTokenError)
    def handle_missing_token(err):
        _log_error(err)
        return _make_error(err, "Authentication token required", 401)

    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(err):
        _log_error(err)
        msg = "Invalid auth token"
        if str(err):
            msg = str(err)
        return _make_error(err, msg, 403)

    @app.errorhandler(NotificationNotFoundError)
    def handle_missing_notification(err):
        _log_error(err)
        return _make_error(err, str(err), 404)

    @app.errorhandler(404)
    def not_found(err):
        return _make_error(err, "Path {} not found.".format(request.path), 404)

    @app.errorhandler(405)
    def handle_not_allowed(err):
        _log_error(err)
        return _make_error(err, "Method not allowed", 405)

    @app.errorhandler(MissingParameterError)
    def handle_missing_params(err):
        _log_error(err)
        return _make_error(err, str(err), 422)

    @app.errorhandler(TokenLookupError)
    def handle_auth_service_error(err):
        _log_error(err)
        return _make_error(err, "Unable to fetch authentication information", 500)

    @app.errorhandler(Exception)
    def general_error(err):
        _log_error(err)
        return _make_error(err, str(err), 500)

    return app


app = create_app()
