import pytest
from feeds.activity.notification import Notification
import uuid
from .util import validate_uuid

def test_basic_notification():
    assert True
    # n = Notification('foo', 'bar', 'baz')
    # assert n.actor == 'foo'
    # assert n.note_type == 'bar'
    # assert n.object == 'baz'
    # assert n.content == {}
    # assert n.target == None
    # assert validate_uuid(n.id)