import os
import configparser
import pytest
import tempfile
import json
import feeds
import test.util as test_util
from .util import test_config
from .mongo_controller import MongoController
import shutil
import time
import re
from requests_mock import ANY as r_mock_ANY


def pytest_sessionstart(session):
    os.environ['AUTH_TOKEN'] = 'foo'
    os.environ['FEEDS_CONFIG'] = os.path.join(os.path.dirname(__file__), 'test.cfg')

def pytest_sessionfinish(session, exitstatus):
    pass

@pytest.fixture(scope="module")
def mongo_notes(mongo):
    test_db_path = os.path.join(os.path.dirname(__file__), "_data", "mongo", "notifications.json")
    with open(test_db_path, "r") as db_file:
        objects = json.loads(db_file.read())
    mongo.client['feeds']['notifications'].insert_many(objects)

@pytest.fixture(scope="module")
def mongo():
    mongoexe = test_util.get_mongo_exe()
    tempdir = test_util.get_temp_dir()
    mongo = MongoController(mongoexe, tempdir)
    print("running MongoDB {} on port {} in dir {}".format(
        mongo.db_version, mongo.port, mongo.temp_dir
    ))
    feeds.config.__config.db_port = mongo.port
    feeds.storage.mongodb.connection._connection = None

    yield mongo
    del_temp = test_util.get_delete_temp_files()
    print("Shutting down MongoDB,{} deleting temp files".format(" not" if not del_temp else ""))
    mongo.destroy(del_temp)
    if del_temp:
        shutil.rmtree(test_util.get_temp_dir())
    # time.sleep(5) # wait for Mongo to go away

@pytest.fixture(scope="module")
def app():
    from feeds.server import create_app
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True
    })

    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

###########################
### USER / AUTH MOCKING
###########################

@pytest.fixture
def mock_valid_user(requests_mock):
    """
    Use this to mock a valid user name sent to the service as a target or recipient of a
    notification. Can use as a fixture as follows:
    def test_something(mock_valid_user):
        mock_valid_user("wjriehl", "Bill Riehl")
        ... continue with test that uses auth. Now wjriehl is the expected user ...
    """
    def auth_valid_user(user_id, user_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/users?list={}'.format(auth_url, user_id),
            text=json.dumps({user_id: user_name}))
    return auth_valid_user

@pytest.fixture
def mock_valid_users(requests_mock):
    """
    Use this to mock several valid users. like this:
    def test_something(mock_valid_users):
        mock_valid_users({"fake_user": "Fake User", "fake2": "Fake User2", ...etc})
        ... continue with test
    TODO: refactor tests to just this throughout and retire mock_valid_user above
    """
    def auth_valid_users(users):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        matcher = re.compile('api/V2/users\?list=')
        requests_mock.register_uri('GET', matcher, text=json.dumps(users))
    return auth_valid_users


@pytest.fixture
def mock_invalid_user(requests_mock):
    """
    Use this to mock an invalid user name being sent to the service as a target or recipient of
    a notification. Use as follows:
    def test_bad_user(mock_invalid_user):
        mock_invalid_user("not_a_real_user")
        ... continue with test. auth will fail, and should return "not_a_real_user" as the user that was attempted ...
    """
    def auth_invalid_user(user_id):
        cfg = test_config()
        requests_mock.get('{}/api/V2/users?list={}'.format(cfg.get('feeds', 'auth-url'), user_id), text="{}")
    return auth_invalid_user

@pytest.fixture
def mock_valid_user_token(requests_mock):
    """
    Use this to mock a valid authenticated request coming from a user (not an admin or service).
    Use the fixture as follows:
    def test_something(mock_valid_user_token):
        mock_valid_user_token('someuser', 'Some User')
        ... continue test ...
    """
    def auth_valid_user_token(user_id, user_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/token'.format(auth_url), json={
            'user': user_id,
            'type': 'Login',
            'name': None
        })
        requests_mock.get('{}/api/V2/me'.format(auth_url), json={
            'customroles': [],
            'display': user_name,
            'user': user_id
        })
    return auth_valid_user_token

@pytest.fixture
def mock_valid_service_token(requests_mock):
    """
    Use this to mock a valid authenticated request coming from a service (not a user).
    Use as follows:
    def test_something(mock_valid_service_token):
        mock_valid_service_token('some_user', 'Some User', 'MyKBaseService')
        ...continue test...
    """
    def auth_valid_service_token(user_id, user_name, service_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/token'.format(auth_url), json={
            'user': user_id,
            'type': 'Service',
            'name': service_name
        })
        requests_mock.get('{}/api/V2/me'.format(auth_url), json={
            'customroles': [],
            'display': user_name,
            'user': user_id
        })
    return auth_valid_service_token

@pytest.fixture
def mock_valid_admin_token(requests_mock):
    """
    Use this to mock a valid authenticated request coming from a Feeds admin (i.e. a user
    with the FEEDS_ADMIN custom role). Use as follows:
        def test_something(mock_valid_admin_token):
            mock_valid_admin_token('some_admin', 'Valid Admin')
            ... rest of test ...
    """
    def auth_valid_admin_token(user_id, user_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/token'.format(auth_url), json={
            'user': user_id,
            'type': 'Login',
            'name': None
        })
        requests_mock.get('{}/api/V2/me'.format(auth_url), json={
            'customroles': ['FEEDS_ADMIN'],
            'display': user_name,
            'user': user_id
        })
    return auth_valid_admin_token

@pytest.fixture
def mock_invalid_user_token(requests_mock):
    """
    Mocks an invalid (for whatever reason) user token. Probably should be treated as present,
    but expired.
    As above, just call it inside your test as:
    mock_invalid_user_token(user_id)
    """
    def auth_invalid_user_token(user_id):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.register_uri('GET', '{}/api/V2/token'.format(auth_url),
            status_code=403,
            json={
                "error": {
                    "appcode": 10020,
                    "apperror": "Invalid token",
                    "httpcode": 403,
                    "httpstatus": "Unauthorized"
                }
            }
        )
    return auth_invalid_user_token

@pytest.fixture
def mock_auth_error(requests_mock):
    cfg = test_config()
    auth_url = cfg.get('feeds', 'auth-url')
    requests_mock.register_uri('GET', '{}/api/V2/token'.format(auth_url),
        status_code=500,
        json={
            "error": {
                "httpcode": 500,
                "httpstatus": "FAIL",
                "apperror": "Something very bad happened, mm'kay?"
            }
        })


##################################
### GENERIC NETWORK ERROR MOCKING
##################################

@pytest.fixture
def mock_network_error(requests_mock):
    """
    Any network call just zonks out with a 500. Simulate big fails when talking to services.
    """
    requests_mock.register_uri(r_mock_ANY, r_mock_ANY,
        status_code=500,
        json={
            "error": {
                "httpcode": 500,
                "httpstatus": "FAIL",
                "apperror": "Your network asplode."
            }
        })


###############################
### GROUPS SERVICE API MOCKING
###############################

@pytest.fixture
def mock_valid_group(requests_mock):
    def valid_group_id(g_id):
        cfg = test_config()
        groups_url = cfg.get('feeds', 'groups-url')
        requests_mock.get("{}/group/{}/exists".format(groups_url, g_id), json={
            "exists": True
        })
    return valid_group_id


@pytest.fixture
def mock_invalid_group(requests_mock):
    def invalid_group_id(g_id):
        cfg = test_config()
        groups_url = cfg.get('feeds', 'groups-url')
        requests_mock.get("{}/group/{}/exists".format(groups_url, g_id), json={
            "exists": False
        })
    return invalid_group_id


@pytest.fixture
def mock_user_groups(requests_mock):
    def user_groups(groups):
        cfg = test_config()
        groups_url = cfg.get('feeds', 'groups-url')
        requests_mock.get("{}/member/".format(groups_url), json=groups)
    return user_groups

###################################
### WORKSPACE SERVICE API MOCKING
###################################

def workspace_info_matcher(req):
    body = json.loads(req.text)
    return body.get("method") == "Workspace.get_workspace_info"

@pytest.fixture
def mock_workspace_info(requests_mock):
    def valid_workspace_info(info):
        cfg = test_config()
        ws_url = cfg.get('feeds', 'workspace-url')
        requests_mock.register_uri("POST", ws_url,
            additional_matcher=workspace_info_matcher,
            json={
                "version": "1.1",
                "result": [info]
            }
        )
    return valid_workspace_info

@pytest.fixture
def mock_workspace_info_error(requests_mock):
    def error_workspace_info(ws_id):
        cfg = test_config()
        ws_url = cfg.get('feeds', 'workspace-url')
        requests_mock.register_uri("POST", ws_url,
            additional_matcher=workspace_info_matcher,
            status_code=500,
            json={
                "version": "1.1",
                "error": {
                    "name": "JSONRPCError",
                    "code": "-32500",
                    "message": "Workspace {} is deleted".format(ws_id),
                    "error": "Long winded exception..."
                }
            }
        )
    return error_workspace_info

@pytest.fixture
def mock_workspace_info_invalid(requests_mock):
    def invalid_workspace_info(ws_id):
        cfg = test_config()
        ws_url = cfg.get('feeds', 'workspace-url')
        requests_mock.register_uri("POST", ws_url,
            additional_matcher=workspace_info_matcher,
            status_code=500,
            json={
                "version": "1.1",
                "error": {
                    "name": "JSONRPCError",
                    "code": "-32500",
                    "message": "No workspace with id {} exists".format(ws_id),
                    "error": "Long winded exception..."
                }
            }
        )
    return invalid_workspace_info


#######################################
### CATALOG/NMS SERVICE API MOCKING ###
#######################################

def nms_brief_info_matcher(req):
    body = json.loads(req.text)
    return body.get("method") == "NarrativeMethodStore.get_method_brief_info"

@pytest.fixture
def mock_app_lookup(requests_mock):
    def app_lookup(app_mapping):
        app_list = list()
        for app in app_mapping:
            if app_mapping[app] is None:
                app_list.append(None)
            else:
                app_list.append({"id": app, "name": app_mapping[app]})
        print("MOCK RESULTS: {}".format(app_list))
        cfg = test_config()
        nms_url = cfg.get('feeds', 'nms-url')
        requests_mock.register_uri("POST", nms_url,
            additional_matcher=nms_brief_info_matcher,
            json={
                "version": "1.1",
                "result": [app_list]
            }
        )
    return app_lookup

@pytest.fixture
def mock_app_lookup_fail(requests_mock):
    cfg = test_config()
    nms_url = cfg.get('feeds', 'nms-url')
    requests_mock.register_uri("POST", nms_url,
        additional_matcher=nms_brief_info_matcher,
        status_code=500,
        json={
            "version": "1.1",
            "error": {
                "name": "JSONRPCError",
                "code": "-32500",
                "message": "Something silly happened.",
                "error": "Long winded explanation..."
            }
        }
    )
