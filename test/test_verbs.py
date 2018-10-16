import pytest
from feeds import verbs

def test_register_verb():
    class TestVerb(verbs.Verb):
        id=666
        infinitive="test"
        past_tense="tested"
    verbs.register(TestVerb)
    assert '666' in verbs._verb_register
    assert verbs._verb_register['666'] == TestVerb
    assert 'test' in verbs._verb_register
    assert verbs._verb_register['test'] == TestVerb
    assert 'tested' in verbs._verb_register
    assert verbs._verb_register['tested'] == TestVerb

def test_register_verb_fail():
    with pytest.raises(TypeError) as e:
        verbs.register(str)
    assert "Can only register Verb subclasses" in str(e.value)

    class CopyId(verbs.Verb):
        id=1
        infinitive='fail'
        past_tense='fail'
    with pytest.raises(ValueError) as e:
        verbs.register(CopyId)
    assert "The verb id '1' is already taken" in str(e.value)

    class CopyInf(verbs.Verb):
        id=1000
        infinitive='invite'
        past_tense='fail'
    with pytest.raises(ValueError) as e:
        verbs.register(CopyInf)
    assert "The verb 'invite' is already registered!" in str(e.value)

    class CopyPT(verbs.Verb):
        id=1000
        infinitive='fail'
        past_tense='invited'
    with pytest.raises(ValueError) as e:
        verbs.register(CopyPT)
    assert "The verb 'invited' is already registered!" in str(e.value)

    class NoId(verbs.Verb):
        infinitive='fail'
        past_tense='fail'
    with pytest.raises(ValueError) as e:
        verbs.register(NoId)
    assert "A verb must have an id" in str(e.value)

    class NoInf(verbs.Verb):
        id=1000
        past_tense='fail'
    with pytest.raises(ValueError) as e:
        verbs.register(NoInf)
    assert "A verb must have an infinitive form" in str(e.value)

    class NoPT(verbs.Verb):
        id=1000
        infinitive='fail'
    with pytest.raises(ValueError) as e:
        verbs.register(NoPT)
    assert "A verb must have a past tense form" in str(e.value)

def test_get_verb():
    v = verbs.get_verb(1)
    v2 = verbs.get_verb('invite')
    v3 = verbs.get_verb('invited')
    assert v.__class__ == v2.__class__ == v3.__class__
    assert v.id == 1
    assert v.infinitive == 'invite'
    assert v.past_tense == 'invited'
    assert str(v) == 'invite'

def test_get_verb_fail():
    with pytest.raises(ValueError) as e:
        verbs.get_verb('fail')
    assert 'Verb "fail" not found' in str(e.value)

    with pytest.raises(AssertionError) as e:
        verbs.get_verb(None)

def test_serialize():
    v = verbs.get_verb('invite')
    assert v.serialize() == 1