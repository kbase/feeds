import pytest
import os
import json
from uuid import uuid4
from feeds.util import epoch_ms
import feeds.config


@pytest.fixture(scope="module")
def mongo_notes(mongo):
    test_db_path = os.path.join(os.path.dirname(__file__), "..", "_data", "mongo", "notifications.json")
    with open(test_db_path, "r") as db_file:
        objects = json.loads(db_file.read())
    mongo.client['feeds']['notifications'].insert_many(objects)


def test_api_root(client):
    response = client.get('/admin/api/V1')
    data = json.loads(response.data)
    assert 'routes' in data
    assert len(data['routes']) == 4

###
# POST /notification/global
###

def test_add_global_notification(client, mock_valid_admin_token, mongo):
    note = {
        "verb": 1,
        "object": "2",
        "level": 1
    }
    mock_valid_admin_token("kbase_admin", "KBase Admin")
    response = client.post(
        "/admin/api/V1/notification/global",
        headers={"Authorization": "token-"+str(uuid4())},
        json=note
    )
    data = json.loads(response.data)
    assert "id" in data

    response = client.get(
        "/api/V1/notification/" + data["id"],
        headers={"Authorization": "token-"+str(uuid4())}
    )
    data = json.loads(response.data)["notification"]
    assert "expires" in data
    assert "created" in data
    assert data["created"] + (feeds.config.get_config().lifespan * 24 * 60 * 60 * 1000) == data["expires"]


def test_add_global_notification_custom_expiration(client, mock_valid_admin_token, mongo):
    expiration = epoch_ms() + 20000
    note = {
        "verb": 1,
        "object": "2",
        "level": 1,
        "expires": expiration
    }
    mock_valid_admin_token("kbase_admin", "KBase Admin")
    response = client.post(
        "/admin/api/V1/notification/global",
        headers={"Authorization": "token-"+str(uuid4())},
        json=note
    )
    data = json.loads(response.data)
    assert "id" in data

    response = client.get(
        "/api/V1/notification/" + data["id"],
        headers={"Authorization": "token-"+str(uuid4())}
    )
    data = json.loads(response.data)["notification"]
    assert "expires" in data
    assert "created" in data
    assert data["expires"] == expiration


def test_add_global_notification_expiration(client, mock_valid_admin_token, mongo):
    note = {
        "verb": 1,
        "object": "2",
        "level": 1
    }
    mock_valid_admin_token("kbase_admin", "KBase Admin")
    response = client.post(
        "/admin/api/V1/notification/global",
        headers={"Authorization": "token-"+str(uuid4())},
        json=note
    )
    data = json.loads(response.data)
    assert "id" in data


def test_add_global_notification_user_auth(client, mock_valid_user_token):
    mock_valid_user_token("not_admin", "Not Admin")
    response = client.post(
        '/admin/api/V1/notification/global',
        headers={"Authorization": "token-"+str(uuid4())}
    )
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"]["http_code"] == 403
    assert data["error"]["message"] == \
        "You do not have permission to create a global notification!"


def test_add_global_notification_invalid_auth(client, mock_invalid_user_token):
    mock_invalid_user_token("test_user")
    response = client.post(
        '/admin/api/V1/notification/global',
        headers={"Authorization": "token-"+str(uuid4())}
    )
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 403
    assert data['error']['message'] == 'Invalid token'


def test_add_global_notification_no_auth(client):
    response = client.post('/admin/api/V1/notification/global')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'


####
# POST /admin/api/V1/notifications/expire
####
@pytest.mark.parametrize("inputs,code,msg", [
    ({"note_ids":[],"external_keys":[], "source": "foo"}, 200, None),
    ({"note_ids":[],"external_keys":[]}, 200, None),
    ({"note_ids":[None],"external_keys":[None]}, 400, "note_ids must be a list of strings"),
    ({"note_ids":["foo"],"external_keys":[None]}, 400, "external_keys must be a list of strings"),
    ({"note_ids": None, "external_keys":[]}, 400, "Expected note_ids to be a list."),
    ({"note_ids":[], "external_keys":None}, 400, "Expected external_keys to be a list."),
    ({"note_ids":[{}], "external_keys":[]}, 400, "note_ids must be a list of strings"),
    ({"note_ids":[], "external_keys":[{}]}, 400, "external_keys must be a list of strings"),
    ({"source": "foo"}, 422, 'Missing parameter "note_ids" or "external_keys"'),
    ("foo!", 400, 'Expected a JSON object as an input.'),
    ({"note_ids":[], "external_keys":["foo"]}, 422,
        'Parameter "source" must be present when expiring notifications by their external keys')
])
def test_expire_notifications_admin_inputs(client, mongo_notes, mock_valid_admin_token,
                                           inputs, code, msg):
    mock_valid_admin_token('kbase_admin', 'KBase Admin')
    header = {"Authorization": "token-"+str(uuid4())}
    response = client.post('/admin/api/V1/notifications/expire', headers=header, json=inputs)
    assert response.status_code == code
    if msg is None:
        return
    assert json.loads(response.data)['error']['message'] == msg


def test_admin_expire_no_auth(client):
    response = client.post('/admin/api/V1/notifications/expire')
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['http_code'] == 401
    assert data['error']['message'] == 'Authentication token required'


def test_admin_expire_user_auth(client, mock_valid_user_token):
    mock_valid_user_token("not_admin", "Not Admin")
    response = client.post(
        '/admin/api/V1/notifications/expire',
        headers={"Authorization": "token-"+str(uuid4())}
    )
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"]["http_code"] == 403
    assert data["error"]["message"] == \
        "Only admins can use this path to expire tokens."


def test_admin_expire_service_auth(client, mock_valid_service_token):
    mock_valid_service_token("service_user", "Service User", "aservice")
    response = client.post(
        '/admin/api/V1/notifications/expire',
        headers={"Authorization": "token-"+str(uuid4())}
    )
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"]["http_code"] == 403
    assert data["error"]["message"] == \
        "Only admins can use this path to expire tokens."


def test_expire_notifications_admin(client, mongo_notes, mock_valid_admin_token, mock_valid_users):
    mock_valid_admin_token("kbase_admin", "KBase Admin")
    mock_valid_users({"kbasetest": "KBase Test Account", "kbase": "KBase"})
    # make a notification
    admin_cred = {"Authorization": "token-"+str(uuid4())}
    note = {
        "verb": 1,
        "level": 1,
        "object": "stuff",
    }
    response = client.post(
        "/admin/api/V1/notification/global",
        headers=admin_cred,
        json=note
    )
    post_return = json.loads(response.data)
    assert 'id' in post_return
    # get its id
    note_id = post_return['id']
    # verify it gets returned from the global stack
    response2 = client.get(
        "/api/V1/notifications/global"
    )
    global_notes = json.loads(response2.data)
    global_ids = [n["id"] for n in global_notes["feed"]]
    assert note_id in global_ids
    # expire it
    response3 = client.post(
        "/admin/api/V1/notifications/expire",
        headers=admin_cred,
        json={"note_ids": [note_id, "fake_id"]}
    )
    expire_return = json.loads(response3.data)
    assert expire_return == {
        "expired": {"note_ids": [note_id], "external_keys": []},
        "unauthorized": {"note_ids": ["fake_id"], "external_keys": []}
    }
    # make sure it doesn't show up any more
    response4 = client.get(
        "/api/V1/notifications/global"
    )
    global_notes = json.loads(response4.data)
    global_ids = [n["id"] for n in global_notes["feed"]]
    assert note_id not in global_ids


def test_expire_notification_admin_from_service(client, mongo_notes, mock_valid_admin_token, mock_valid_service_token, mock_valid_user):
    source = "a_service"
    external_key = "foobarkey"
    mock_valid_user("kbasetest", "KBase Test")
    mock_valid_service_token("user", "Name", source)
    # service creates two notifications - one with external key
    service_cred = {"Authorization": "token-"+str(uuid4())}
    note = {
        "actor": "kbasetest",
        "verb": 1,
        "level": 1,
        "object": "stuff",
        "users": ["kbasetest"],
        "source": source,
        "target": ["kbasetest"]
    }
    response = client.post(
        "/api/V1/notification",
        headers = service_cred,
        json=note
    )
    post_return = json.loads(response.data)
    assert "id" in post_return
    note_id = post_return["id"]
    note["external_key"] = external_key
    response2 = client.post(
        "/api/V1/notification",
        headers=service_cred,
        json=note
    )
    post_return2 = json.loads(response2.data)
    assert "id" in post_return2
    # now invoke the admin to delete both of those. Should succeed.
    mock_valid_admin_token("some_admin", "Some Admin")
    admin_cred = {"Authorization": "token-"+str(uuid4())}
    exp_response = client.post(
        "/admin/api/V1/notifications/expire",
        headers=admin_cred,
        json={
            "note_ids": [note_id],
            "external_keys": [external_key],
            "source": source
        }
    )
    exp_data = json.loads(exp_response.data)
    assert exp_data == {
        "expired": {
            "note_ids": [note_id],
            "external_keys": [external_key]
        },
        "unauthorized": {
            "note_ids": [],
            "external_keys": []
        }
    }
