import os
import tempfile
import json
import pytest
from pprint import pprint
from .conftest import test_config
cfg = test_config()

@pytest.mark.parametrize('path', (
    '/api/V1/notifications',
    '/api/V1/notifications?',
    '/api/V1/notification/some_note_id'
))
def test_server_get_paths_noauth(client, path):
    response = client.get(path)
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'].get('http_code') == 403
    assert data['error'].get('http_status') == 'Forbidden'
    assert 'Authentication token required' in data['error'].get('message')

@pytest.mark.parametrize('path', (
    '/api/V1/notification',
    '/api/V1/notification/global',
    '/api/V1/notifications/see',
    '/api/V1/notifications/unsee'
))
def test_server_post_paths_noauth(client, path):
    response = client.post(path)
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'].get('http_code') == 403
    assert data['error'].get('http_status') == 'Forbidden'
    assert 'Authentication token required' in data['error'].get('message')

def test_root(client):
    response = client.get('/')
    data = json.loads(response.data)
    print(data)
    assert 'servertime' in data
    assert 'service' in data and data['service'] == 'Notification Feeds Service'
    assert 'version' in data

def test_api_root(client):
    response = client.get('/api/V1')
    data = json.loads(response.data)
    assert 'routes' in data
    assert len(data['routes']) == 8

def test_permissions_noauth(client, requests_mock):
    response = client.get('/permissions')
    data = json.loads(response.data)
    assert 'token' in data
    assert data['token'] == {'service': None, 'user': None, 'admin': False}
    assert 'permissions' in data
    assert data['permissions'] == {'GET': ['/notifications/global'], 'POST': []}

def test_permissions_user(client, requests_mock, mock_valid_user_token):
    user_id = 'a_user'
    user_name = 'A User'
    mock_valid_user_token(user_id, user_name)
    response = client.get('/permissions', headers={'Authorization': 'foo'})
    data = json.loads(response.data)
    print("TEST USER PERMISSIONS --- {}".format(data))

def test_permissions_service(client, requests_mock):
    test_name = 'SomeService'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'type': 'Service', 'name': test_name}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({}))

def test_permissions_admin(client, requests_mock):
    test_name = 'SomeService'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'type': 'Service', 'name': test_name}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({}))

