import json
import pytest
import mongomock
from pprint import pprint
from uuid import uuid4


def test_api_root(client):
    response = client.get('/api/V1')
    data = json.loads(response.data)
    assert 'routes' in data
    assert len(data['routes']) == 8

###
# GET /notifications
###

def test_get_notifications(client, mock_valid_user_token):
    user_id="wjriehl"
    user_name="William Riehl"
    mock_valid_user_token(user_id, user_name)
    response = client.get('/api/V1/notifications', headers={"Authorization": "token-"+str(uuid4())})
    # Got the fake db in _data/mongo/notifications.json
    data = json.loads(response.data)
    for note in data['global'] + data['user']:
        _validate_notification(note)

def test_get_notifications_no_auth(client):
    response = client.get('/api/V1/notifications')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_get_notifications_invalid_auth(client, mock_invalid_user_token):
    mock_invalid_user_token("test_user")
    response = client.post('/api/V1/notification', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Invalid token'


###
# POST /notification
###

def test_post_notification_ok(client, mock_valid_service_token):
    pass

def test_post_notification_no_auth(client):
    response = client.post('/api/V1/notification')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_post_notification_user_auth(client, mock_valid_user_token):
    mock_valid_user_token("test_user", "Test User")
    response = client.post('/api/V1/notification', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Authentication token must be a Service token.'

def test_post_notification_invalid_auth(client, mock_invalid_user_token):
    mock_invalid_user_token("test_user")
    response = client.post('/api/V1/notification', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Invalid token'


###
# POST /notification/global
###

def test_add_global_notification(client, mock_valid_admin_token):
    pass

def test_add_global_notification_user_auth(client, mock_valid_user_token):
    pass

def test_add_global_notification_invalid_auth(client, mock_invalid_user_token):
    mock_invalid_user_token("test_user")
    response = client.post('/api/V1/notification/global', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Invalid token'


def test_add_global_notification_no_auth(client):
    response = client.post('/api/V1/notification/global')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

###
# GET /notifications/global
###

def test_get_global_notifications(client):
    pass

###
# GET /notification/<note_id>
###

@pytest.mark.parametrize("test_id,expected", [
    ("fake_id", "fake result")
])
def test_get_single_notification(client, mock_valid_user_token, test_id, expected):
    pass

def test_get_single_notification_no_auth(client):
    response = client.get('/api/V1/notification/12345')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_get_single_notification_invalid_auth(client, mock_invalid_user_token):
    mock_invalid_user_token("test_user")
    response = client.get('/api/V1/notification/12345', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Invalid token'

def test_get_single_notification_wrong_user(client, mock_valid_user_token):
    mock_valid_user_token("wrong_user", "Test User")
    response = client.get('/api/V1/notification/1', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    pprint(data)
    assert 'error' in data
    assert data['error']['http_code'] == 404
    assert data['error']['message'] == 'Cannot find notification with id 1.'

###
# POST /notifications/see
###

def test_mark_notifications_seen(client, mock_valid_user_token):
    pass

def test_mark_notifications_seen_no_auth(client):
    response = client.post('/api/V1/notifications/see')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_mark_notifications_seen_invalid_auth(client, mock_invalid_user_token):
    mock_invalid_user_token('test_user')
    response = client.post('/api/V1/notifications/see', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403

###
# POST /notifications/unsee
###

def test_mark_notifications_unseen(client, mock_valid_user_token):
    pass

def test_mark_notifications_unseen_no_auth(client):
    response = client.post('/api/V1/notifications/unsee')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_mark_notifications_unseen_invalid_auth(client, mock_invalid_user_token):
    pass


def _validate_notification(note):
    """
    Validates the structure of a user's notification.
    Expects a dict.
    """
    required_keys = ["id", "actor", "verb", "object", "target", "created", "expires", "source"]
    for k in required_keys:
        assert k in note
