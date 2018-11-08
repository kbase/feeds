import os
import tempfile
import json
import pytest
from pprint import pprint

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
    assert 'servertime' in data
    assert 'service' in data and data['service'] == 'Notification Feeds Service'
    assert 'version' in data

def test_api_root(client):
    response = client.get('/api/V1')
    data = json.loads(response.data)
    assert 'routes' in data
    assert len(data['routes']) == 8
