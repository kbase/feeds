import os
import tempfile
import json
import pytest
from pprint import pprint
from .conftest import test_config
from uuid import uuid4
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


def test_permissions_noauth(client, requests_mock):
    response = client.get('/permissions')
    data = json.loads(response.data)
    assert 'token' in data
    assert data['token'] == {'service': None, 'user': None, 'admin': False}
    assert 'permissions' in data
    assert data['permissions'] == {'GET': ['/api/V1/notifications/global'], 'POST': []}


def test_permissions_user(client, requests_mock, mock_valid_user_token):
    user_id = 'a_user'
    user_name = 'A User'
    mock_valid_user_token(user_id, user_name)
    response = client.get('/permissions', headers={'Authorization': 'test_token'+str(uuid4())})
    data = json.loads(response.data)
    assert 'token' in data
    assert data['token'] == {'service': None, 'user': user_id, 'admin': False}
    assert 'permissions' in data
    assert 'GET' in data['permissions']
    valid_gets = set(['/api/V1/notifications/global', '/api/V1/notifications', '/api/V1/notification/<note_id>'])
    assert valid_gets == set(data['permissions']['GET'])
    valid_posts = set(['/api/V1/notifications/see', '/api/V1/notifications/unsee'])
    assert valid_posts == set(data['permissions']['POST'])


def test_permissions_service(client, requests_mock, mock_valid_service_token):
    service_name = 'SomeService'
    user_id = 'service_user'
    user_name = 'Service User'
    mock_valid_service_token(user_id, user_name, service_name)
    response = client.get('/permissions', headers={'Authorization': 'serv_token-'+str(uuid4())})
    data = json.loads(response.data)
    assert 'token' in data
    assert data['token'] == {'service': service_name, 'user': user_id, 'admin': False}
    assert 'permissions' in data
    assert 'GET' in data['permissions']
    valid_gets = set(['/api/V1/notifications/global', '/api/V1/notifications', '/api/V1/notification/<note_id>'])
    assert valid_gets == set(data['permissions']['GET'])
    valid_posts = set(['/api/V1/notifications/see', '/api/V1/notifications/unsee', '/api/V1/notification'])
    assert valid_posts == set(data['permissions']['POST'])


def test_permissions_admin(client, requests_mock, mock_valid_admin_token):
    user_id = 'service_user'
    user_name = 'Service User'
    mock_valid_admin_token(user_id, user_name)
    response = client.get('/permissions', headers={'Authorization': 'admin_token-'+str(uuid4())})
    data = json.loads(response.data)
    assert 'token' in data
    assert data['token'] == {'service': None, 'user': user_id, 'admin': True}
    assert 'permissions' in data
    assert 'GET' in data['permissions']
    valid_gets = set(['/api/V1/notifications/global', '/api/V1/notifications', '/api/V1/notification/<note_id>'])
    assert valid_gets == set(data['permissions']['GET'])
    valid_posts = set(['/api/V1/notifications/see', '/api/V1/notifications/unsee', '/api/V1/notification/global'])
    assert valid_posts == set(data['permissions']['POST'])


def test_permissions_bad_token(client, mock_invalid_user_token):
    user_id = 'bad_user'
    mock_invalid_user_token(user_id)
    response = client.get('/permissions', headers={'Authorization': 'bad_token-'+str(uuid4())})
    data = json.loads(response.data)
    assert 'token' in data
    assert data['token'] == {'service': None, 'user': None, 'admin': False}
    assert 'permissions' in data
    assert data['permissions'] == {'GET': ['/api/V1/notifications/global'], 'POST': []}
