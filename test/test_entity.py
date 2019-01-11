import pytest
from feeds.entity import (
    Entity,
    STR_SEPARATOR
)
from feeds.exceptions import (
    EntityValidationError,
    EntityNameError
)

@pytest.mark.parametrize("e_id,e_type", [
    ("foo", "user"),
    ("foo", "workspace"),
    ("foo", "narrative"),
    ("foo", "group"),
    ("foo", "admin"),
    ("foo", "job")
])
def test_entity_init_ok(e_id, e_type):
    e = Entity(e_id, e_type)
    assert e.id == e_id
    assert e.type == e_type

@pytest.mark.parametrize("bad_type,expect_except,msg", [
    ("bad", EntityValidationError, "is not a valid type for an Entity"),
    (123, AssertionError, "entity type must be a string"),
    ({}, AssertionError, "entity type must be a string"),
    (("foo", "bar"), AssertionError, "entity type must be a string")
])
def test_entity_init_bad_type(bad_type, expect_except, msg):
    with pytest.raises(expect_except) as e:
        Entity("foo", bad_type)
    assert msg in str(e)


def test_entity_init_autovalidate(mock_valid_users):
    user_id = "fake"
    user_name = "Fake User"
    mock_valid_users({user_id: user_name})
    e = Entity(user_id, "user", auto_validate=True)
    assert e.id == user_id
    assert e.type == "user"


def test_entity_init_autovalidate_fail(mock_invalid_user):
    user_id = "bad_user"
    mock_invalid_user(user_id)
    with pytest.raises(EntityValidationError) as e:
        Entity(user_id, "user", auto_validate=True)
    assert "Entity of type user with id {} is not valid".format(user_id)


def test_entity_validate_user_ok(mock_valid_users):
    mock_valid_users({"fake": "Fake User"})
    e = Entity("fake", "user")
    assert e.validate() is True

    e = Entity("some_admin", "admin")
    assert e.validate() is True


def test_entity_validate_group_ok(mock_valid_group):
    g_id = "mygroup"
    mock_valid_group(g_id)
    e = Entity(g_id, "group")
    assert e.validate() is True


def test_entity_validate_workspace_ok(mock_workspace_info):
    ws_id = 5
    info = [5, "A_Workspace", "owner", "Timestamp", 18, "a", "n", "unlocked", {}]
    mock_workspace_info(info)
    e = Entity(ws_id, "workspace")
    assert e.validate() is True


def test_entity_validate_workspace_false(mock_workspace_info_invalid):
    ws_id = 5
    mock_workspace_info_invalid(ws_id)
    e = Entity(ws_id, "workspace")
    assert e.validate() is False


def test_entity_validate_workspace_fail(mock_workspace_info_error):
    ws_id = 5
    mock_workspace_info_error(ws_id)
    e = Entity(ws_id, "workspace")
    assert e.validate() is False


def test_entity_validate_narrative_ok(mock_workspace_info):
    ws_id = 5
    info = [5, "A_Workspace", "owner", "Timestamp", 18, "a", "n", "unlocked", {"narrative": "1", "narrative_nice_name": "My Narrative"}]
    mock_workspace_info(info)
    e = Entity(ws_id, "narrative")
    assert e.validate() is True


def test_entity_validate_narrative_fail(mock_workspace_info_invalid):
    ws_id = 5
    mock_workspace_info_invalid(ws_id)
    e = Entity(ws_id, "narrative")
    assert e.validate() is False


def test_entity_validate_job_ok():
    pass


def test_entity_validate_user_fail(mock_invalid_user):
    user_id = "not_a_user"
    mock_invalid_user(user_id)
    e = Entity(user_id, "user")
    assert e.validate() is False


@pytest.mark.parametrize("e_id,e_type,name", [
    ("foo1", "user", "Foo User"),
    ("foo2", "workspace", "Foo Workspace"),
    ("foo3", "narrative", "Foo Narrative"),
    ("foo4", "group", "Foo Group"),
    ("foo5", "admin", "Foo Admin"),
    ("foo6", "job", "Foo Job")
])
def test_entity_to_dict(e_id, e_type, name):
    e = Entity(e_id, e_type, name=name)
    d = {"id": e_id, "type": e_type}
    d_name = d.copy()
    d_name["name"] = name
    assert e.to_dict() == d
    assert e.to_dict(with_name=True) == d_name


def test_entity_from_dict():
    d = {"id": "foo", "type": "user"}
    e = Entity.from_dict(d)
    assert e.to_dict() == d
    assert e.id == d['id']
    assert e.type == d['type']

    d = {"id": "bar", "type": "group", "name": "Bar Group"}
    e = Entity.from_dict(d)
    assert e.to_dict(with_name=True) == d
    assert e.id == d['id']
    assert e.type == d['type']
    assert e.name == d['name']


@pytest.mark.parametrize("d,err,msg", [
    ({"id": "wat", "type": "nope"}, EntityValidationError, "is not a valid type for an Entity"),
    ({"type": "user"}, EntityValidationError, "An Entity requires an id!"),
    ({"id": "foo"}, EntityValidationError, "An Entity requires a type!"),
    ("some str", AssertionError, "from_dict requires a dictionary input!")
])
def test_entity_from_dict_fail(d, err, msg):
    with pytest.raises(err) as e:
        Entity.from_dict(d)
    assert msg in str(e)


@pytest.mark.parametrize("e_id,e_type,name", [
    ("foo", "user", None),
    ("bar", "group", "Bar Group")
])
def test_entity_str(e_id, e_type, name):
    e = Entity(e_id, e_type, name=name)
    s = str(e)
    assert s == e_type + STR_SEPARATOR + e_id


def test_entity_from_str():
    eid = "foo"
    etype = "user"
    s = etype + STR_SEPARATOR + eid
    e = Entity.from_str(s)
    assert e.id == eid
    assert e.type == etype


@pytest.mark.parametrize("s,err,msg", [
    ("nope::stuff", EntityValidationError, "is not a valid type for an Entity"),
    ("123::foo", EntityValidationError, "is not a valid type for an Entity"),
    (None, AssertionError, "input must be a string"),
    ("foo", EntityValidationError, "could not be resolved into an Entity"),
    ("::", AssertionError, "An Entity must have an id!")
])
def test_entity_from_str_fail(s, err, msg):
    with pytest.raises(err) as e:
        Entity.from_str(s)
    assert msg in str(e)


def test_entity_hash():
    """
    Don't really care what the hash is, as long as:
    1. it's an integer
    2. it's consistent
    """
    eid = "foo"
    etype = "user"
    eid2 = "bar"
    etype2 = "group"
    e1 = Entity(eid, etype)
    e1_copy = Entity(eid, etype)
    e2 = Entity(eid2, etype2)
    e3 = Entity(eid, etype2)
    assert isinstance(hash(e1), int)
    assert hash(e1) == hash(e1)
    assert hash(e1) == hash(e1_copy)
    assert hash(e1) != hash(e2)
    assert hash(e1) != hash(e3)


def test_entity_eq():
    eid1 = "foo"
    eid2 = "bar"
    etype1 = "user"
    etype2 = "group"
    e11 = Entity(eid1, etype1)
    e11_2 = Entity(eid1, etype1)
    e12 = Entity(eid1, etype2)
    e21 = Entity(eid2, etype1)
    e22 = Entity(eid2, etype2)
    assert e11 == e11
    assert e11 == e11_2
    assert e12 != e11
    assert e11 != e12
    assert e11 != e22
    assert e21 != e11
    assert e22 == Entity.from_dict({"id": eid2, "type": etype2})


def test_entity_repr():
    e = Entity("foo", "user")
    r = repr(e)
    assert r == 'Entity("foo", "user")'


def test_entity_fetch_name_user(mock_valid_users):
    user_name = "Fake User"
    user_id = "fake"
    mock_valid_users({user_id: user_name})
    e = Entity(user_id, "user")
    e._fetch_name()
    assert e.name == user_name


def test_entity_name_getter_user_ok(mock_valid_users):
    user_name = "Some User"
    user_id = "some_user"
    mock_valid_users({user_id: user_name})
    e = Entity(user_id, "user")
    assert e.name == user_name


def test_entity_name_getter_user_fail(mock_invalid_user):
    user_id = "bad_user"
    mock_invalid_user(user_id)
    e = Entity(user_id, "user")
    with pytest.raises(EntityNameError) as err:
        x = e.name
    assert "Unable to find name for user id: {}".format(user_id) in str(err)


def test_entity_name_getter_auth_fail(mock_network_error):
    e = Entity("a_user", "user")
    with pytest.raises(EntityNameError) as error:
        x = e.name
    assert "Unable to find name for user id" in str(error)


def test_entity_name_getter_group_fail():
    pass


def test_entity_name_getter_workspace_fail(mock_workspace_info_invalid):
    ws_id = 8
    mock_workspace_info_invalid(ws_id)
    e = Entity(ws_id, "workspace")
    with pytest.raises(EntityNameError) as err:
        x = e.name
    assert "Unable to find name for workspace id: {}".format(ws_id) in str(err)


def test_entity_name_getter_workspace_error(mock_workspace_info_error):
    ws_id = 8
    mock_workspace_info_error(ws_id)
    e = Entity(ws_id, "workspace")
    with pytest.raises(EntityNameError) as err:
        x = e.name
    assert "Unable to find name for workspace id: {}".format(ws_id) in str(err)


def test_entity_name_getter_narrative_fail(mock_workspace_info_invalid):
    ws_id = 8
    mock_workspace_info_invalid(ws_id)
    e = Entity(ws_id, "narrative")
    with pytest.raises(EntityNameError) as err:
        x = e.name
    assert "Unable to find name for narrative id: {}".format(ws_id) in str(err)


def test_entity_name_getter_narrative_error(mock_workspace_info_error):
    ws_id = 8
    mock_workspace_info_error(ws_id)
    e = Entity(ws_id, "narrative")
    with pytest.raises(EntityNameError) as err:
        x = e.name
    assert "Unable to find name for narrative id: {}".format(ws_id) in str(err)


def test_entity_name_getter_job_fail():
    pass


def test_entity_name_setter():
    user_name = "A User"
    user_id = "a_user"
    e = Entity(user_id, "user")
    e.name = user_name
    assert e.name == user_name


def test_entity_fetch_name_ws(mock_workspace_info):
    ws_id = 6
    info = [6, "A_Workspace", "owner", "Timestamp", 18, "a", "n", "unlocked", {"narrative": "1", "narrative_nice_name": "My Narrative"}]
    mock_workspace_info(info)
    e = Entity(ws_id, "workspace")
    assert e.name == info[1]


def test_entity_fetch_name_narr(mock_workspace_info):
    ws_id = 7
    info = [7, "A_Workspace", "owner", "Timestamp", 18, "a", "n", "unlocked", {"narrative": "1", "narrative_nice_name": "My Narrative"}]
    mock_workspace_info(info)
    e = Entity(ws_id, "narrative")
    assert e.name == info[8]["narrative_nice_name"]


def test_entity_fetch_name_group():
    pass


def test_entity_fetch_name_job():
    pass
