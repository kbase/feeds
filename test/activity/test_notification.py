import pytest
import json
from feeds.activity.notification import Notification
import uuid
from feeds.util import epoch_ms
from ..conftest import test_config
from ..util import assert_is_uuid
from feeds.exceptions import (
    MissingVerbError,
    MissingLevelError,
    InvalidExpirationError,
    InvalidNotificationError
)

cfg = test_config()

# some dummy "good" inputs for testing
actor = "test_actor"
verb_inf = "invite"
verb_past = "invited"
verb_id = 1
note_object = "foo"
source = "groups"
level_name = "warning"
level_id = 2
target = ["target_actor"]
context = {"some": "context"}
expires = epoch_ms() + (10 * 24 * 60 * 60 * 1000) # 10 days
external_key = "an_external_key"

def assert_note_ok(note, **kwargs):
    keys = [
        'actor', 'object', 'source', 'target', 'context', 'expires', 'external_key'
    ]
    for k in keys:
        if k in kwargs:
            assert getattr(note, k) == kwargs[k]
    if 'verb_id' in kwargs:
        assert note.verb.id == int(kwargs['verb_id'])
    if 'verb_inf' in kwargs:
        assert note.verb.infinitive == kwargs['verb_inf']
    if 'level_id' in kwargs:
        assert note.level.id == int(kwargs['level_id'])
    if 'level_name' in kwargs:
        assert note.level.name == kwargs['level_name']
    if 'expires' not in kwargs:
        assert note.expires == note.created + (int(cfg.get('feeds', 'lifespan')) * 24 * 60 * 60 * 1000)
    assert note.created < note.expires
    assert_is_uuid(note.id)

def test_note_new_ok_no_kwargs():
    note = Notification(actor, verb_inf, note_object, source)
    assert_note_ok(note, actor=actor, verb_inf=verb_inf, object=note_object, source=source)

def test_note_new_diff_levels():
    assert_args = {
        "actor": actor,
        "verb_inf": verb_inf,
        "object": note_object,
        "source": source
    }
    for name in ['alert', 'warning', 'request', 'error']:
        note = Notification(actor, verb_inf, note_object, source, level=name)
        test_args = assert_args.copy()
        test_args['level_name'] = name
        assert_note_ok(note, **test_args)
    for id_ in ['1', '2', '3', '4']:
        note = Notification(actor, verb_inf, note_object, source, level=id_)
        test_args = assert_args.copy()
        test_args['level_id'] = id_
        assert_note_ok(note, **test_args)


def test_note_new_target():
    note = Notification(actor, verb_inf, note_object, source, target=target)
    assert_note_ok(note, actor=actor, verb_inf=verb_inf,
                   object=note_object, source=source, target=target)


def test_note_new_context():
    note = Notification(actor, verb_inf, note_object, source, context=context)
    assert_note_ok(note, actor=actor, verb_inf=verb_inf,
                   object=note_object, source=source, context=context)


def test_note_new_expiration():
    note = Notification(actor, verb_inf, note_object, source, expires=expires)
    assert_note_ok(note, actor=actor, verb_inf=verb_inf,
                   object=note_object, source=source, expires=expires)


def test_note_new_external_key():
    note = Notification(actor, verb_inf, note_object, source, external_key=external_key)
    assert_note_ok(note, actor=actor, verb_inf=verb_inf,
                   object=note_object, source=source, external_key=external_key)


def test_note_new_bad_actor():
    # TODO: Should only fail on validate - shouldn't do a lookup whenever a new note is made.
    # also, shouldn't be None.
    with pytest.raises(AssertionError) as e:
        Notification(None, verb_inf, note_object, source)
    assert "actor must not be None" in str(e.value)


def test_note_new_bad_verb():
    with pytest.raises(AssertionError) as e:
        Notification(actor, None, note_object, source)
    assert "verb must not be None" in str(e.value)

    with pytest.raises(MissingVerbError) as e:
        Notification(actor, "foobar", note_object, source)
    assert 'Verb "foobar" not found' in str(e.value)


def test_note_new_bad_object():
    # TODO: Also test object validation itself later.
    with pytest.raises(AssertionError) as e:
        Notification(actor, verb_inf, None, source)
    assert 'note_object must not be None' in str(e.value)

def test_note_new_bad_source():
    # TODO: Validate sources as being real.
    with pytest.raises(AssertionError) as e:
        Notification(actor, verb_inf, note_object, None)
    assert 'source must not be None' in str(e.value)


def test_note_new_bad_level():
    with pytest.raises(AssertionError) as e:
        Notification(actor, verb_inf, note_object, source, level=None)
    assert "level must not be None" in str(e.value)

    with pytest.raises(MissingLevelError) as e:
        Notification(actor, verb_inf, note_object, source, level="foobar")
    assert 'Level "foobar" not found' in str(e.value)


def test_note_new_bad_target():
    bad_targets = [{}, "foo", 123, False]
    for bad in bad_targets:
        with pytest.raises(AssertionError) as e:
            Notification(actor, verb_inf, note_object, source, target=bad)
        assert "target must be either a list or None" in str(e.value)


def test_note_new_bad_context():
    bad_context = [[], "foo", 123, False]
    for bad in bad_context:
        with pytest.raises(AssertionError) as e:
            Notification(actor, verb_inf, note_object, source, context=bad)
        assert "context must be either a dict or None" in str(e.value)


def test_note_new_bad_expires():
    bad_expires = ["foo", {}, []]
    for bad in bad_expires:
        with pytest.raises(InvalidExpirationError) as e:
            Notification(actor, verb_inf, note_object, source, expires=bad)
        assert "Expiration time should be the number of milliseconds" in str(e.value)
    bad_expires = [123, True, False]
    for bad in bad_expires:
        with pytest.raises(InvalidExpirationError) as e:
            Notification(actor, verb_inf, note_object, source, expires=bad)
        assert "Notifications should expire sometime after they are created" in str(e.value)


def test_validate_ok(requests_mock):
    user_id = "foo"
    user_display = "Foo Bar"
    requests_mock.get('{}/api/V2/users?list={}'.format(cfg.get('feeds', 'auth-url'), user_id), text=json.dumps({user_id: user_display}))
    note = Notification(user_id, verb_inf, note_object, source)
    # If this doesn't throw any errors, then it passes!
    note.validate()


def test_validate_bad(requests_mock):
    user_id = "foo"
    requests_mock.get('{}/api/V2/users?list={}'.format(cfg.get('feeds', 'auth-url'), user_id), text=json.dumps({}))
    note = Notification(user_id, verb_inf, note_object, source)
    # If this doesn't throw any errors, then it passes!
    note.validate()


def test_default_lifespan():
    note = Notification(actor, verb_inf, note_object, source)
    lifespan = int(cfg.get('feeds', 'lifespan'))
    assert note.expires - note.created == lifespan * 24 * 60 * 60 * 1000


def test_to_dict():
    note = Notification(actor, verb_inf, note_object, source, level=level_name)
    d = note.to_dict()
    assert d["actor"] == actor
    assert d["verb"] == verb_id
    assert d["object"] == note_object
    assert d["source"] == source
    assert isinstance(d["expires"], int) and d["expires"] == note.expires
    assert isinstance(d["created"], int) and d["created"] == note.created
    assert d["target"] is None
    assert d["context"] is None
    assert d["level"] == level_id
    assert d["external_key"] is None


def test_user_view():
    note = Notification(actor, verb_inf, note_object, source, level=level_id)
    v = note.user_view()
    assert v["actor"] == actor
    assert v["verb"] == verb_past
    assert v["object"] == note_object
    assert v["source"] == source
    assert isinstance(v["expires"], int) and v["expires"] == note.expires
    assert isinstance(v["created"], int) and v["created"] == note.created
    assert "target" not in v
    assert v["context"] is None
    assert v["level"] == level_name
    assert "external_key" in v
    assert v["external_key"] is None


def test_from_dict():
    act_id = str(uuid.uuid4())
    verb = [verb_id, str(verb_id), verb_inf, verb_past]
    level = [level_id, level_name, str(level_id)]
    d = {
        "actor": actor,
        "object": note_object,
        "source": source,
        "expires": 1234567890111,
        "created": 1234567890000,
        "target": target,
        "context": context,
        "external_key": external_key,
        "id": act_id
    }
    for v in verb:
        for l in level:
            note_d = d.copy()
            note_d.update({'level': l, 'verb': v})
            note = Notification.from_dict(note_d)
            assert_note_ok(note, **note_d)


def test_from_dict_missing_keys():
    d = {
        "actor": actor
    }
    with pytest.raises(InvalidNotificationError) as e:
        Notification.from_dict(d)
    assert "Missing keys" in str(e.value)

    with pytest.raises(InvalidNotificationError) as e:
        Notification.from_dict(None)
    assert "Can only run 'from_dict' on a dict" in str(e.value)


def test_serialization():
    note = Notification(actor, verb_inf, note_object, source, level=level_id)
    serial = note.serialize()
    json_serial = json.loads(serial)
    assert "i" in json_serial
    assert_is_uuid(json_serial['i'])
    assert "a" in json_serial and json_serial['a'] == actor
    assert "v" in json_serial and json_serial['v'] == verb_id
    assert "o" in json_serial and json_serial['o'] == note_object
    assert "s" in json_serial and json_serial['s'] == source
    assert "l" in json_serial and json_serial['l'] == level_id
    assert "c" in json_serial and json_serial['c'] == note.created
    assert "e" in json_serial and json_serial['e'] == note.expires
    assert "n" in json_serial and json_serial['n'] == None
    assert "x" in json_serial and json_serial['x'] == None
    assert "t" in json_serial and json_serial['t'] == None


def test_serialization_all_kwargs():
    note = Notification(actor, verb_inf, note_object, source, level=level_id,
                        target=target, external_key=external_key, context=context)
    serial = note.serialize()
    json_serial = json.loads(serial)
    assert "i" in json_serial
    assert_is_uuid(json_serial['i'])
    assert "a" in json_serial and json_serial['a'] == actor
    assert "v" in json_serial and json_serial['v'] == verb_id
    assert "o" in json_serial and json_serial['o'] == note_object
    assert "s" in json_serial and json_serial['s'] == source
    assert "l" in json_serial and json_serial['l'] == level_id
    assert "c" in json_serial and json_serial['c'] == note.created
    assert "e" in json_serial and json_serial['e'] == note.expires
    assert "n" in json_serial and json_serial['n'] == context
    assert "x" in json_serial and json_serial['x'] == external_key
    assert "t" in json_serial and json_serial['t'] == target


def test_deserialization():
    note = Notification(actor, verb_inf, note_object, source, level=level_id,
                        target=target, external_key=external_key, context=context)
    serial = note.serialize()
    note2 = Notification.deserialize(serial)
    assert note2.id == note.id
    assert note2.actor == note.actor
    assert note2.verb.id == note.verb.id
    assert note2.object == note.object
    assert note2.source == note.source
    assert note2.level.id == note.level.id
    assert note2.target == note.target
    assert note2.external_key == note.external_key
    assert note2.context == note.context


def test_deserialize_bad():
    with pytest.raises(InvalidNotificationError) as e:
        Notification.deserialize(None)
    assert "Can't deserialize an input of 'None'" in str(e.value)

    with pytest.raises(InvalidNotificationError) as e:
        Notification.deserialize(json.dumps({'a': actor}))
    assert "Missing keys" in str(e.value)

    with pytest.raises(InvalidNotificationError) as e:
        Notification.deserialize("foo")
    assert "Can only deserialize a JSON string" in str(e.value)