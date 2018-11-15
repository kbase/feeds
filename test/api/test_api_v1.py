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

def test_get_notifications(client, mock_valid_user_token):
    user_id="wjriehl"
    user_name="William Riehl"
    mock_valid_user_token(user_id, user_name)
    response = client.get('/api/V1/notifications', headers={"Authorization": "token-"+str(uuid4())})
    pprint(json.loads(response.data))

def test_get_notifications_no_auth(client):
    pass

def test_get_notifications_invalid_auth(client, mock_invalid_user_token):
    pass

def test_post_notification_ok(client, mock_valid_service_token):
    pass

def test_post_notification_no_auth(client):
    pass

def test_post_notification_user_auth(client, mock_valid_user_token):
    pass

def test_post_notification_invalid_auth(client, mock_invalid_user_token):
    pass

def test_add_global_notification(client, mock_valid_admin_token):
    pass

def test_add_global_notification_user_auth(client, mock_valid_user_token):
    pass

def test_add_global_notification_invalid_auth(client, mock_invalid_user_token):
    pass

def test_add_global_notification_no_auth(client):
    pass

def test_get_global_notifications(client):
    pass

@pytest.mark.parametrize("test_id,expected", [
    ("fake_id", "fake result")
])
def test_get_single_notification(client, mock_valid_user_token, test_id, expected):
    pass

def test_get_single_notification_no_auth(client):
    pass

def test_get_single_notification_invalid_auth(client, mock_invalid_user_token):
    pass

def test_mark_notifications_seen(client, mock_valid_user_token):
    pass

def test_mark_notifications_seen_no_auth(client):
    pass

def test_mark_notifications_seen_invalid_auth(client, mock_invalid_user_token):
    pass

def test_mark_notifications_unseen(client, mock_valid_user_token):
    pass

def test_mark_notifications_unseen_no_auth(client):
    pass

def test_mark_notifications_unseen_invalid_auth(client, mock_invalid_user_token):
    pass
