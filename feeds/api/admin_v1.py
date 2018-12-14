import flask
from flask import request
from flask_cors import cross_origin
import json

from feeds.activity.notification import Notification
from feeds.managers.notification_manager import NotificationManager
from feeds.feeds.notification.notification_feed import NotificationFeed
from feeds.auth import (
    get_auth_token,
    is_feeds_admin
)
from feeds.exceptions import (
    InvalidTokenError
)
from feeds.config import get_config
from .util import (
    parse_notification_params,
    parse_expire_notifications_params
)

cfg = get_config()
admin_v1 = flask.Blueprint('admin_v1', __name__)


@admin_v1.route('/', methods=['GET'])
def root():
    resp = {
        'routes': {
            'root': 'GET /admin/api/V1',
            'add_global_notification': 'POST /admin/api/V1/notification/global',
            'get_specific_notification': 'GET /admin/api/V1/notification/<note_id>',
            'expire_notifications': 'POST /admin/api/V1/notifications/expire'
        }
    }
    return flask.jsonify(resp)


@admin_v1.route('/notification/global', methods=['POST'])
@cross_origin()
def add_global_notification():
    token = get_auth_token(request)
    if not is_feeds_admin(token):
        raise InvalidTokenError("You do not have permission to create a global notification!")

    params = parse_notification_params(json.loads(request.get_data()), is_global=True)
    new_note = Notification(
        'kbase',
        params.get('verb'),
        params.get('object'),
        'kbase',
        params.get('level'),
        context=params.get('context'),
        expires=params.get('expires')
    )
    global_feed = NotificationFeed(cfg.global_feed)
    global_feed.add_notification(new_note)
    return (flask.jsonify({'id': new_note.id}), 200)


@admin_v1.route('/notifications/expire', methods=['POST'])
@cross_origin()
def expire_notifications():
    """
    Notifications can be forced to expire (set their expiration time to now).
    This route (/admin/api/V1/notifications/expire) can only be used by admins. There's
    a separate route for services (see api_v1.expire_notifications)
    Expects JSON in the body formatted like this:
    {
        "note_ids": [notification ids],
        "external_keys": [keys],
        "source": source_service
    }
    The id keys are both optional, but at least one must be present. Any combination of external
    keys or ids is acceptable, even if they're the same notification.

    Admins can expire any notification, including globals. Expiring global notifications
    (via note_ids) is possible without a source field for an admin, but if external_keys are
    used, then source MUST be present. Both the source and external key are used together to
    find the notification.

    This returns the following:
    {
        "expired": {
            "note_ids": [],
            "external_keys": []
        }
        "unauthorized": {
            "note_ids": [],
            "external_keys": []
        }
    }
    This should just return the same lists of values that were input, just shuffled to
    their final status.

    """
    token = get_auth_token(request)
    if not is_feeds_admin(token):
        raise InvalidTokenError("Only admins can use this path to expire tokens.")

    data = parse_expire_notifications_params(json.loads(request.get_data()), is_admin=True)
    manager = NotificationManager()
    result = manager.expire_notifications(
        data.get('note_ids', []),
        data.get('external_keys', []),
        source=data.get('source'),
        is_admin=True
    )
    return (flask.jsonify(result), 200)
