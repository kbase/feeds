import pytest
import requests
import json
import os
import uuid
from feeds.external_api.auth import (
    validate_user_token,
    validate_service_token,
    get_auth_token,
    is_feeds_admin
)
import feeds.external_api.auth as auth
from ..util import test_config
from feeds.exceptions import InvalidTokenError

cfg = test_config()




def test_validate_service_token_ok(requests_mock):

    # test service token
    token = 'fake_token' + str(uuid.uuid4())
    test_name = 'test_name'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'type': 'Service', 'name': test_name}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({}))
    assert (validate_service_token(token) == test_name)


def test_validate_service_token_fail(requests_mock):

    token = 'fake_token' + str(uuid.uuid4())
    test_user = 'test_user'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'user': test_user}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'customroles': []}))

    with pytest.raises(InvalidTokenError) as e:
        validate_service_token(token)
    assert "Authentication token must be a Service token." in str(e.value)


def test_is_feeds_admin_ok(requests_mock):
    # test service token - should fail
    token = 'fake_token' + str(uuid.uuid4())
    test_name = 'test_name'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'type': 'Service', 'name': test_name}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({}))
    assert is_feeds_admin(token) == False

    # test feeds admin user token
    token = 'fake_token' + str(uuid.uuid4())
    test_user = 'test_user'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'user': test_user}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'customroles': ['FEEDS_ADMIN']}))
    assert is_feeds_admin(token)

    # test common user token
    token = 'fake_token' + str(uuid.uuid4())
    test_user = 'test_user'
    requests_mock.get('{}/api/V2/token'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'user': test_user}))
    requests_mock.get('{}/api/V2/me'.format(cfg.get('feeds', 'auth-url')),
                      text=json.dumps({'customroles': []}))
    assert not is_feeds_admin(token)


def test_valid_token_cache(mock_valid_user_token):
    user = "some_user"
    name = "Some User"
    token = "some_token" + str(uuid.uuid4())
    mock_valid_user_token(user, name, [])

    assert token not in auth.__token_cache
    info = validate_user_token(token)
    assert info == user

    assert token in auth.__token_cache
    assert auth.__token_cache.get(token)['user'] == user
    info = validate_user_token(token)
    assert info == user


def test_expired_token_cache(mock_valid_user_token):
    user = "some_user"
    name = "Some User"
    token = "some_token" + str(uuid.uuid4())
    mock_valid_user_token(user, name, [], expires=0)

    assert token not in auth.__token_cache
    info = validate_user_token(token)
    assert info == user

    with pytest.raises(KeyError):
        info = auth.__token_cache[token]


def test_bad_token_cache(mock_invalid_user_token):
    user = "some_user"
    token = "bad_token" + str(uuid.uuid4())
    mock_invalid_user_token(user)

    assert token not in auth.__bad_token_cache
    with pytest.raises(InvalidTokenError):
        validate_user_token(token)
    assert token in auth.__bad_token_cache

    with pytest.raises(InvalidTokenError) as e:
        validate_user_token(token)
    assert "Invalid token" in str(e.value)


def test_bad_token_cache_size(mock_invalid_user_token):
    user = "some_user"
    token = "bad_token" + str(uuid.uuid4())
    mock_invalid_user_token(user)

    assert token not in auth.__bad_token_cache
    with pytest.raises(InvalidTokenError):
        validate_user_token(token)
    assert token in auth.__bad_token_cache

    for i in range(10000):
        t = "bad" + str(i)
        try:
            validate_user_token(t)
        except:
            pass

    assert token not in auth.__bad_token_cache
