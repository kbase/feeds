import os
import configparser
import pytest
import tempfile
import json

def pytest_sessionstart(session):
    os.environ['AUTH_TOKEN'] = 'foo'
    os.environ['FEEDS_CONFIG'] = os.path.join(os.path.dirname(__file__), 'test.cfg')

def pytest_sessionfinish(session, exitstatus):
    pass

def test_config():
    """
    Returns a ConfigParser.
    Because I'm lazy.
    """
    cfg = configparser.ConfigParser()
    with open(os.environ['FEEDS_CONFIG'], 'r') as f:
        cfg.read_file(f)
    return cfg

@pytest.fixture
def app():
    from feeds.server import create_app
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True
    })

    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def mock_valid_user(requests_mock):
    """
    Use this to mock a valid user. Can use as a fixture as follows:
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
def mock_invalid_user(requests_mock):
    """
    User this to mock an invalid user. Use as follows:
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
    def auth_valid_user_token(user_id, user_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/token'.format(auth_url), text=json.dumps({
            'user': user_id,
            'type': 'Login',
            'name': None
        }))
        requests_mock.get('{}/api/V2/me'.format(auth_url), text=json.dumps({
            'customroles': [],
            'display': user_name,
            'user': user_id
        }))
    return auth_valid_user_token

@pytest.fixture
def mock_valid_service_token(requests_mock):
    def auth_valid_service_token(user_id, user_name, service_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/token'.format(auth_url), text=json.dumps({
            'user': user_id,
            'type': 'Service',
            'name': service_name
        }))
        requests_mock.get('{}/api/V2/me'.format(auth_url), text=json.dumps({
            'customroles': [],
            'display': user_name,
            'user': user_id
        }))
    return auth_valid_service_token

@pytest.fixture
def mock_valid_admin_token(request_mock):
    def auth_valid_admin_token(user_id, user_name):
        cfg = test_config()
        auth_url = cfg.get('feeds', 'auth-url')
        requests_mock.get('{}/api/V2/token'.format(auth_url), text=json.dumps({
            'user': user_id,
            'type': 'Login',
            'name': None
        }))
        requests_mock.get('{}/api/V2/me'.format(auth_url), text=json.dumps({
            'customroles': ['FEEDS_ADMIN'],
            'display': user_name,
            'user': user_id
        }))
    return auth_valid_admin_token
