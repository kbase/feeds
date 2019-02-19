import pytest
from feeds.entity.types.service import (
    ServiceType,
    DEFAULT_SERVICE
)
from feeds.exceptions import EntityNameError

@pytest.mark.parametrize("name,expected", [
    ("groups", "Groups"),
    ("groupsservice", "Groups"),
    ("Foo", DEFAULT_SERVICE),
    ("workspace", "Workspace"),
    ("ws", "Workspace")
])
def test_get_name_from_id(name, expected):
    assert ServiceType.get_name_from_id(name, None) == expected


def test_get_names_from_ids():
    std = {
        "groups": "Groups",
        "groupsservice": "Groups",
        "Foo": DEFAULT_SERVICE,
        "Nope": DEFAULT_SERVICE,
        "ws": "Workspace"
    }
    names = ServiceType.get_names_from_ids(list(std.keys()), None)
    for n in std:
        assert n in names
        assert names[n] == std[n]


@pytest.mark.parametrize("service_id,expected", [
    ("groups", True),
    ("groupsservice", True),
    ("Foo", False),
    ("Bar", False),
    ("workspace", True),
    ("ws", True)
])
def test_validate_id(service_id, expected):
    assert ServiceType.validate_id(service_id, None) is expected
