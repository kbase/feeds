import pytest
import feeds.notification_level as level
from feeds.exceptions import (
    MissingLevelError
)

def test_register_level_ok():
    class TestLevel(level.Level):
        id=666
        name="test"
    level.register(TestLevel)
    assert '666' in level._level_register
    assert level._level_register['666'] == TestLevel
    assert 'test' in level._level_register
    assert level._level_register['test'] == TestLevel

def test_register_level_bad():
    class NoId(level.Level):
        id=None
        name="noid"

    with pytest.raises(ValueError) as e:
        level.register(NoId)
    assert "A level must have an id" in str(e.value)

    class NoName(level.Level):
        id=667

    with pytest.raises(ValueError) as e:
        level.register(NoName)
    assert "A level must have a name" in str(e.value)

    class DuplicateId(level.Level):
        id='1'
        name='duplicate'

    with pytest.raises(ValueError) as e:
        level.register(DuplicateId)
    assert "The level id '1' is already taken by alert" in str(e.value)

    class DuplicateName(level.Level):
        id=668
        name="warning"

    with pytest.raises(ValueError) as e:
        level.register(DuplicateName)
    assert "The level 'warning' is already registered" in str(e.value)

    with pytest.raises(TypeError) as e:
        level.register(str)
    assert "Can only register Level subclasses" in str(e.value)

    with pytest.raises(ValueError) as e:
        level.register(level.Alert)
    assert "The level id '1' is already taken by alert" in str(e.value)


def test_get_level():
    l = level.get_level('warning')
    assert isinstance(l, level.Warning)
    assert l.id == level.Warning.id
    assert l.name == level.Warning.name

    missing = "not_a_real_level"
    with pytest.raises(MissingLevelError) as e:
        level.get_level(missing)
    assert 'Level "{}" not found'.format(missing) in str(e.value)


def test_translate_level():
    l = level.Alert()
    l_trans = level.translate_level(l)
    assert isinstance(l_trans, level.Alert)

    l = level.translate_level(1)
    assert isinstance(l, level.Alert)
    assert l.name == 'alert'

    l = level.translate_level('1')
    assert isinstance(l, level.Alert)
    assert l.name == 'alert'

    l = level.translate_level('alert')
    assert isinstance(l, level.Alert)

    with pytest.raises(MissingLevelError) as e:
        level.translate_level('foo')
    assert 'Level "foo" not found' in str(e.value)

    with pytest.raises(TypeError) as e:
        level.translate_level([])
    assert 'Must be either a subclass of Level or a string' in str(e.value)
