import pytest
from feeds.external_api.groups import (
    get_user_groups,
    get_group_names,
    validate_group_id
)
from feeds.exceptions import GroupsError

def test_validate_group_id_valid(mock_valid_group):
    g = "a_group"
    mock_valid_group(g)
    assert validate_group_id(g)

def test_validate_group_id_invalid(mock_invalid_group):
    g = "another_group"
    mock_invalid_group(g)
    assert validate_group_id(g) is False

def test_validate_group_id_fail(mock_network_error):
    with pytest.raises(GroupsError) as e:
        validate_group_id("fail")
    assert "Unable to fetch group information" in str(e)

def test_get_user_groups(mock_user_groups):
    dummy_ret = [{"id": "g1", "name": "Group Name"}]
    mock_user_groups(dummy_ret)
    groups = get_user_groups("some_token")
    assert groups == dummy_ret

def test_get_user_groups_fail(mock_network_error):
    with pytest.raises(GroupsError) as e:
        get_user_groups("some_token")
    assert "Unable to fetch group information" in str(e)
