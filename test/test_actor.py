import pytest
import requests
import json
import os
from feeds.actor import validate_actor
from .conftest import test_config
from feeds.exceptions import InvalidActorError

cfg = test_config()
def test_validate_actor(requests_mock):
    user_id = "foo"
    user_display = "Foo Bar"
    requests_mock.get('{}/api/V2/users?list={}'.format(cfg.get('feeds', 'auth-url'), user_id), text=json.dumps({user_id: user_display}))
    assert validate_actor(user_id)


def test_validate_actor_fail(requests_mock):
    user_id = "foo2"
    requests_mock.get('{}/api/V2/users?list={}'.format(cfg.get('feeds', 'auth-url'), user_id), text=json.dumps({}))
    with pytest.raises(InvalidActorError) as e:
        validate_actor(user_id)
    assert "Actor '{}' is not a real user".format(user_id) in str(e.value)
