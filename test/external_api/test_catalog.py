import pytest
from feeds.external_api.catalog import (
    get_app_name,
    get_app_names
)
from feeds.exceptions import CatalogError

def test_get_app_name(mock_app_lookup):
    app_ids_mock = {
        "mod1/meth1": "Method 1",
        "mod2/meth2": "Method 2",
        "mod4/meth4": None
    }
    app_mappings_std = {
        "mod1.meth1": "Method 1",
        "mod2.meth2": "Method 2",
        "mod2/meth2": "Method 2",
        "mod3.meth3": None,
        "mod4.meth4": None
    }
    mock_app_lookup(app_ids_mock)
    for i in app_mappings_std:
        assert get_app_name(i) == app_mappings_std[i]


def test_get_app_name_fail(mock_app_lookup_fail):
    with pytest.raises(CatalogError) as e:
        get_app_name("wat")
    assert "An error occurred while retrieving app names" in str(e)


def test_get_app_names(mock_app_lookup):
    app_ids_mock = {
        "mod1/meth1": "Method 1",
        "mod2/meth2": "Method 2"
    }
    app_mappings_std = {
        "mod1.meth1": "Method 1",
        "mod2.meth2": "Method 2",
        "mod2/meth2": "Method 2",
        "mod3.meth3": None
    }
    mock_app_lookup(app_ids_mock)
    names = get_app_names(list(app_mappings_std.keys()))
    for i in app_mappings_std:
        assert names[i] == app_mappings_std[i]


def test_get_app_names_fail(mock_app_lookup_fail):
    with pytest.raises(CatalogError) as e:
        get_app_names(["wat"])
    assert "An error occurred while retrieving app names" in str(e)
