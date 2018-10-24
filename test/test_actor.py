import pytest
import requests
import json
import os
from feeds.actor import validate_actor
from .conftest import test_config

def test_validate_actor(requests_mock):
    cfg = test_config()
    user_id = "foo"
    user_display = "Foo Bar"
    requests_mock.get('{}/api/V2/users?list={}'.format(cfg.get('feeds', 'auth-url'), user_id), text=json.dumps({user_id: user_display}))
    assert user_id in validate_actor(user_id)