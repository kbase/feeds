import json
import pytest
from pprint import pprint
from uuid import uuid4
import test.util as test_util
from test.mongo_controller import MongoController
import shutil
import os
import feeds.config


@pytest.fixture(scope="module")
def mongo_notes(mongo):
    test_db_path = os.path.join(os.path.dirname(__file__), "..", "_data", "mongo", "notifications.json")
    with open(test_db_path, "r") as db_file:
        objects = json.loads(db_file.read())
    mongo.client['feeds']['notifications'].insert_many(objects)

def test_api_root(client):
    response = client.get('/api/V1')
    data = json.loads(response.data)
    assert 'routes' in data
    assert len(data['routes']) == 8

###
# GET /notifications
###


def test_get_notifications(client, mock_valid_user_token, mongo_notes):
    user_id="test_user"
    user_name="Test User"
    mock_valid_user_token(user_id, user_name)
    response = client.get('/api/V1/notifications', headers={"Authorization": "token-"+str(uuid4())})
    # Got the fake db in _data/mongo/notifications.json
    data = json.loads(response.data)
    assert len(data['user']) == 7
    for note in data['global'] + data['user']:
        _validate_notification(note)

@pytest.mark.parametrize("filters,expected", [
    ("n=2", ['7', '6']),
    ("n=10", ['7', '6', '5', '4', '3', '2', '1']),
    ("rev=1", ['1', '2', '3', '4', '5', '6', '7']),
    ("seen=1", ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']),
    ("n=2&seen=1", ['10', '9']),
    ("v=1", ['2', '1']),
    ("v=invite", ['2', '1']),
    ("v=invited", ['2', '1']),
    ("l=alert", ['3', '2', '1']),
    ("l=1", ['3', '2', '1'])
])
def test_get_notifications_filtered(client, mock_valid_user_token, filters, expected):
    user_id="test_user"
    user_name="Test User"
    mock_valid_user_token(user_id, user_name)
    route = '/api/V1/notifications?' + filters
    response = client.get(route, headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert len(data['user']) == len(expected)
    note_order = [n['id'] for n in data['user']]
    assert note_order == expected

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

def test_post_notification_ok(client, mock_valid_service_token, mock_valid_user_token, mock_valid_user):
    service = "a_service"
    test_user = "test_note"
    test_actor = "test_actor"
    mock_valid_user(test_actor, "Test Actor")
    mock_valid_user(test_user, "Test User")
    mock_valid_service_token("user", "pw", service)
    note = {
        "actor": test_actor,
        "target": [test_user],
        "verb": 1,
        "level": 1,
        "object": "stuff",
        "source": service
    }
    response = client.post(
        "/api/V1/notification",
        headers={"Authorization": "token-"+str(uuid4())},
        json=note
    )
    post_return = json.loads(response.data)
    assert 'id' in post_return
    note_id = post_return['id']
    mock_valid_user_token(test_user, "Some Name")
    response = client.get("/api/V1/notifications", headers={"Authorization": "token-"+str(uuid4())})
    data_return = json.loads(response.data)
    assert len(data_return['user']) == 1
    assert data_return['user'][0]['id'] == note_id


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
    note = {
        "verb": 1,
        "object": "2",
        "level": 1
    }
    mock_valid_admin_token("kbase_admin", "KBase Admin")
    response = client.post(
        "/api/V1/notification/global",
        headers={"Authorization": "token-"+str(uuid4())},
        json=note
    )
    data = json.loads(response.data)
    assert "id" in data

def test_add_global_notification_user_auth(client, mock_valid_user_token):
    mock_valid_user_token("not_admin", "Not Admin")
    response = client.post('/api/V1/notification/global', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"]["http_code"] == 403
    assert data["error"]["message"] == "You do not have permission to create a global notification!"

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
    response = client.get('/api/V1/notifications/global')
    data = json.loads(response.data)
    assert len(data) >= 1 and data[-1]["id"] == "global-1"

###
# GET /notification/<note_id>
###

def test_get_single_notification(client, mock_valid_user_token):
    test_ids = ['1', '8']
    mock_valid_user_token("test_user", "Test User")
    auth = {"Authorization": "token-"+str(uuid4())}
    for id_ in test_ids:
        response = client.get("/api/V1/notification/" + id_, headers=auth)
        result = json.loads(response.data)
        assert "notification" in result
        note = result["notification"]
        assert "id" in note and note["id"] == id_

def test_get_single_notification_no_auth(client, mongo_notes):
    response = client.get('/api/V1/notification/12345')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_get_single_notification_invalid_auth(client, mongo_notes, mock_invalid_user_token):
    mock_invalid_user_token("test_user")
    response = client.get('/api/V1/notification/12345', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Invalid token'

def test_get_single_notification_wrong_user(client, mongo_notes, mock_valid_user_token):
    mock_valid_user_token("wrong_user", "Test User")
    response = client.get('/api/V1/notification/1', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 404
    assert data['error']['message'] == 'Cannot find notification with id 1.'

###
# POST /notifications/see
###

def test_mark_notifications_seen(client, mongo_notes, mock_valid_user_token):
    note_id = 'see-test'
    mock_valid_user_token("test_see", "Test Seer")
    auth = {"Authorization": "token-"+str(uuid4())}
    response = client.post(
        "/api/V1/notifications/see",
        json={"note_ids": [note_id]},
        headers=auth
    )
    data = json.loads(response.data)
    assert 'seen_notes' in data
    assert 'unauthorized_notes' in data
    assert note_id in data['seen_notes']
    response = client.get('/api/V1/notification/' + note_id, headers=auth)
    data = json.loads(response.data)
    print(data)
    assert data['notification']['id'] == note_id
    assert data['notification']['seen'] == True

def test_mark_notes_seen_not_allowed(client, mongo_notes, mock_valid_user_token):
    note_id = "not-a-real-note"
    mock_valid_user_token("test_see", "Test Seer")
    auth = {"Authorization": "token-"+str(uuid4())}
    response = client.post(
        "/api/V1/notifications/see",
        json={"note_ids": [note_id]},
        headers=auth
    )
    data = json.loads(response.data)
    assert 'seen_notes' in data
    assert 'unauthorized_notes' in data
    assert note_id in data['unauthorized_notes']

def test_mark_notifications_seen_no_auth(client, mongo_notes):
    response = client.post('/api/V1/notifications/see')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_mark_notifications_seen_invalid_auth(client, mongo_notes, mock_invalid_user_token):
    mock_invalid_user_token('test_user')
    response = client.post('/api/V1/notifications/see', headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403

@pytest.mark.parametrize("params,expected_error", [
    ("foo", (400, "Expected a JSON object as an input.")),
    ({"note_id": "wat"}, (422, "Missing parameter note_ids")),
    ({"note_ids": "not_a_list"}, (400, "Expected a List object as note_ids."))
])
def test_mark_notifications_seen_errors(client, mock_valid_user_token, params, expected_error):
    mock_valid_user_token("some_user", "Some User")
    auth={"Authorization": "token-"+str(uuid4())}
    response = client.post(
        "/api/V1/notifications/see",
        headers=auth,
        json=params
    )
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"]["http_code"] == expected_error[0]
    assert data["error"]["message"] == expected_error[1]

###
# POST /notifications/unsee
###

def test_mark_notifications_unseen(client, mongo_notes, mock_valid_user_token):
    note_id = 'unsee-test'
    mock_valid_user_token("test_unsee", "Test Unseer")
    auth = {"Authorization": "token-"+str(uuid4())}
    response = client.post(
        "/api/V1/notifications/unsee",
        json={"note_ids": [note_id]},
        headers=auth
    )
    data = json.loads(response.data)
    assert 'unseen_notes' in data
    assert 'unauthorized_notes' in data
    assert note_id in data['unseen_notes']
    response = client.get('/api/V1/notification/' + note_id, headers=auth)
    data = json.loads(response.data)
    assert data['notification']['id'] == note_id
    assert data['notification']['seen'] == False

def test_mark_notes_unseen_not_allowed(client, mongo_notes, mock_valid_user_token):
    note_id = "not-a-real-note"
    mock_valid_user_token("test_unsee", "Test Unseer")
    auth = {"Authorization": "token-"+str(uuid4())}
    response = client.post(
        "/api/V1/notifications/unsee",
        json={"note_ids": [note_id]},
        headers=auth
    )
    data = json.loads(response.data)
    assert 'unseen_notes' in data
    assert 'unauthorized_notes' in data
    assert note_id in data['unauthorized_notes']

def test_mark_notifications_unseen_no_auth(client, mongo_notes):
    response = client.post('/api/V1/notifications/unsee')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'

def test_mark_notifications_unseen_invalid_auth(client, mongo_notes, mock_invalid_user_token):
    mock_invalid_user_token('fake_user')
    response = client.post('/api/V1/notifications/unsee', headers={"Authorization": "bad_token-"+str(uuid4())})
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403


def _validate_notification(note):
    """
    Validates the structure of a user's notification.
    Expects a dict.
    """
    required_keys = ["id", "actor", "verb", "object", "target", "created", "expires", "source"]
    for k in required_keys:
        assert k in note
