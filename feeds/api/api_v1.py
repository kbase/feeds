import flask
from flask import request
from flask_cors import cross_origin
import json

from feeds.activity.notification import Notification
from feeds.managers.notification_manager import NotificationManager
from feeds.feeds.notification.notification_feed import NotificationFeed
from feeds.auth import (
    validate_user_token,
    validate_service_token,
    get_auth_token,
    is_feeds_admin
)
from feeds.exceptions import (
    InvalidTokenError,
    IllegalParameterError,
    MissingParameterError,
    NotificationNotFoundError
)
from feeds.config import get_config
from feeds.logger import log
from feeds.notification_level import translate_level
from feeds.verbs import translate_verb

cfg = get_config()
api_v1 = flask.Blueprint('api_v1', __name__)


@api_v1.route('/', methods=['GET'])
def root():
    resp = {
        'routes': {
            'root': 'GET /',
            'add_notification': 'POST /notification',
            'add_global_notification': 'POST /notification/global',
            'get_notifications': 'GET /notifications',
            'get_global_notifications': 'GET /notifications/global',
            'get_specific_notification': 'GET /notification/<note_id>',
            'mark_notifications_seen': 'POST /notifications/see',
            'mark_notifications_unseen': 'POST /notifications/unsee'
        }
    }
    return flask.jsonify(resp)


@api_v1.route('/notifications', methods=['GET'])
@cross_origin()
def get_notifications():
    """
    General flow should be:
    1. validate/authenticate user
    2. make user feed object
    3. query user feed for most recent, based on params
    """
    max_notes = request.args.get('n', default=10, type=int)

    rev_sort = request.args.get('rev', default=0, type=int)
    rev_sort = False if rev_sort == 0 else True

    level_filter_input = request.args.get('l', default=None, type=str)
    level_filter = None
    if level_filter_input is not None:
        level_filter = translate_level(level_filter_input)

    verb_filter_input = request.args.get('v', default=None, type=str)
    verb_filter = None
    if verb_filter_input is not None:
        verb_filter = translate_verb(verb_filter_input)

    include_seen = request.args.get('seen', default=0, type=int)
    include_seen = False if include_seen == 0 else True
    user_id = validate_user_token(get_auth_token(request))
    log(__name__, 'Getting feed for {}'.format(user_id))
    feed = NotificationFeed(user_id)
    user_notes = feed.get_notifications(
        count=max_notes, include_seen=include_seen, level=level_filter,
        verb=verb_filter, reverse=rev_sort, user_view=True
    )

    # fetch the globals
    global_feed = NotificationFeed(cfg.global_feed)
    global_notes = global_feed.get_notifications(count=max_notes, user_view=True)
    return_vals = {
        "user": user_notes,
        "global": global_notes
    }
    return (flask.jsonify(return_vals), 200)


@api_v1.route('/notification', methods=['POST'])
@cross_origin()
def add_notification():
    """
    Adds a new notification for other users to see.
    Form data requires the following:
    * `actor` - a user or org id.
    * `type` - one of the type keywords (see below, TBD (as of 10/8))
    * `target` - optional, a user or org id. - always receives this notification
    * `object` - object of the notice. For invitations, the group to be invited to.
        For narratives, the narrative UPA.
    * `level` - alert, error, warning, or request.
    * `content` - optional, content of the notification, otherwise it'll be
        autogenerated from the info above.
    * `global` - true or false. If true, gets added to the global notification
        feed and everyone gets a copy.

    This also requires a service token as an Authorization header.
    Once validated, will be used as the Source of the notification,
    and used in logic to determine which feeds get notified.
    """
    token = get_auth_token(request)
    try:
        service = validate_service_token(token)
    except InvalidTokenError:
        if cfg.debug:
            if not is_feeds_admin(token):
                raise InvalidTokenError('Auth token must be either a Service token '
                                        'or from a user with the FEEDS_ADMIN role!')
        else:
            raise
    log(__name__, request.get_data())
    params = _get_notification_params(json.loads(request.get_data()))
    # create a Notification from params.
    new_note = Notification(
        params.get('actor'),
        params.get('verb'),
        params.get('object'),
        params.get('source'),
        params.get('level'),
        target=params.get('target', []),
        context=params.get('context'),
        expires=params.get('expires'),
        external_key=params.get('external_key'),
        users=params.get('users', [])
    )
    # pass it to the NotificationManager to dole out to its audience feeds.
    manager = NotificationManager()
    manager.add_notification(new_note)
    # on success, return the notification id and info.
    return (flask.jsonify({'id': new_note.id}), 200)


@api_v1.route('/notification/global', methods=['POST'])
@cross_origin()
def add_global_notification():
    token = get_auth_token(request)
    if not is_feeds_admin(token):
        raise InvalidTokenError("You do not have permission to create a global notification!")

    params = _get_notification_params(json.loads(request.get_data()), is_global=True)
    new_note = Notification(
        'kbase',
        params.get('verb'),
        params.get('object'),
        'kbase',
        params.get('level'),
        context=params.get('context')
    )
    global_feed = NotificationFeed(cfg.global_feed)
    global_feed.add_notification(new_note)
    return (flask.jsonify({'id': new_note.id}), 200)


@api_v1.route('/notifications/global', methods=['GET'])
@cross_origin()
def get_global_notifications():
    global_feed = NotificationFeed(cfg.global_feed)
    global_notes = global_feed.get_notifications(user_view=True)
    return flask.jsonify(global_notes)


@api_v1.route('/notification/<note_id>', methods=['GET'])
@cross_origin()
def get_single_notification(note_id):
    """
    Should only return the note with that id if it's in the user's feed.
    """
    user_id = validate_user_token(get_auth_token(request))
    feed = NotificationFeed(user_id)
    try:
        note = feed.get_notification(note_id)
    except NotificationNotFoundError:
        note = NotificationFeed(cfg.global_feed).get_notification(note_id)
    return (flask.jsonify({'notification': note.user_view()}), 200)


@api_v1.route('/notifications/unsee', methods=['POST'])
@cross_origin()
def mark_notifications_unseen():
    """
    Form data should have a list of notification ids to mark as unseen.
    If any of these do not have the user's id (from the token) on the list,
    raise an error.
    Any of these ids that are global, do nothing... for now.
    """

    user_id = validate_user_token(get_auth_token(request))

    params = _get_mark_notification_params(json.loads(request.get_data()))
    note_ids = params.get('note_ids')

    feed = NotificationFeed(user_id)
    unauthorized_notes = list()
    for note_id in note_ids:
        try:
            feed.get_notification(note_id)
        except NotificationNotFoundError:
            unauthorized_notes.append(note_id)

    unseen_notes = list(set(note_ids) - set(unauthorized_notes))
    feed.mark_activities(unseen_notes, seen=False)

    return (flask.jsonify({'unseen_notes': unseen_notes,
                           'unauthorized_notes': unauthorized_notes}), 200)


@api_v1.route('/notifications/see', methods=['POST'])
@cross_origin()
def mark_notifications_seen():
    """
    Form data should have a list of notification ids to mark as seen.
    If any of these do not have the user's id (from the token) on the list,
    raise an error.
    Any of these ids that are global, do nothing... for now.
    """

    user_id = validate_user_token(get_auth_token(request))

    params = _get_mark_notification_params(json.loads(request.get_data()))
    note_ids = params.get('note_ids')

    feed = NotificationFeed(user_id)
    unauthorized_notes = list()
    for note_id in note_ids:
        try:
            feed.get_notification(note_id)
        except NotificationNotFoundError:
            unauthorized_notes.append(note_id)

    seen_notes = list(set(note_ids) - set(unauthorized_notes))
    feed.mark_activities(seen_notes, seen=True)

    return (flask.jsonify({'seen_notes': seen_notes,
                           'unauthorized_notes': unauthorized_notes}), 200)


def _get_mark_notification_params(params):
    if not isinstance(params, dict):
        raise IllegalParameterError('Expected a JSON object as an input.')

    if 'note_ids' not in params:
        raise MissingParameterError("Missing parameter note_ids")

    if not isinstance(params.get('note_ids'), list):
        raise IllegalParameterError('Expected a List object as note_ids.')

    return params


def _get_notification_params(params, is_global=False):
    """
    Parses and verifies all the notification params are present.
    Raises a MissingParameter error otherwise.
    """
    # * `actor` - a user or org id.
    # * `type` - one of the type keywords (see below, TBD (as of 10/8))
    # * `target` - optional, a user or org id. - always receives this notification
    # * `object` - object of the notice. For invitations, the group to be invited to.
    #   For narratives, the narrative UPA.
    # * `level` - alert, error, warning, or request.
    # * `context` - optional, context of the notification, otherwise it'll be
    #   autogenerated from the info above.

    if not isinstance(params, dict):
        raise IllegalParameterError('Expected a JSON object as an input.')
    required_list = ['verb', 'object', 'level']
    if not is_global:
        required_list = required_list + ['actor', 'target', 'source']
    missing = [r for r in required_list if r not in params]
    if missing:
        raise MissingParameterError("Missing parameter{} - {}".format(
            "s" if len(missing) > 1 else '',
            ", ".join(missing)
        ))
    # TODO - add more checks
    return params
