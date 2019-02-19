import pytest
import requests
import json
import os
from feeds.actor import (
    validate_actor,
    actor_ids_to_names
)
from feeds.exceptions import InvalidActorError
from .util import test_config

cfg = test_config()
def test_validate_actor(mock_valid_user):
    user_id = "foo"
    user_display = "Foo Bar"
    mock_valid_user(user_id, user_display)
    assert validate_actor(user_id)


def test_validate_actor_fail(mock_invalid_user):
    user_id = "foo2"
    mock_invalid_user(user_id)
    with pytest.raises(InvalidActorError) as e:
        validate_actor(user_id)
    assert "Actor '{}' is not a real user".format(user_id) in str(e.value)


def test_actor_ids_to_names(mock_valid_users):
    users = {"fake": "Fake User", "fake2": "Fake User2", "fake3": None}
    mock_valid_users(users)
    names = actor_ids_to_names(list(users.keys()))
    for n in users:
        if users[n] is not None:
            assert names[n] == {"type": "user", "name": users[n]}
        else:
            assert names[n] is None
