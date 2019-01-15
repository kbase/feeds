import pytest
from feeds.entity.types.app import AppType
from feeds.exceptions import EntityNameError

def test_get_name_from_id(mock_app_lookup):
    app_ids = {"mod1/app1": "App 1", "mod2/app2": "App 2"}
    mock_app_lookup(app_ids)
    assert AppType.get_name_from_id("mod1.app1") == "App 1"
    assert AppType.get_name_from_id("mod1/app1") == "App 1"
    assert AppType.get_name_from_id("not_real") is None


def test_get_name_from_id_fail(mock_network_error):
    with pytest.raises(EntityNameError) as e:
        AppType.get_name_from_id("foo")
    assert "Unable to find name for app id: foo" in str(e)


def test_get_names_from_ids(mock_app_lookup):
    app_ids = {
        "mod1/app1": "App 1",
        "mod2/app2": "App 2"
    }
    app_stds = {
        "mod1.app1": "App 1",
        "mod2.app2": "App 2"
    }
    mock_app_lookup(app_ids)
    app_list = ["mod1.app1", "mod2.app2", "mod3.app3"]
    names = AppType.get_names_from_ids(app_list)
    for app in app_list:
        assert app in names
        assert names[app] == app_stds.get(app)


def test_get_names_from_ids_fail(mock_network_error):
    with pytest.raises(EntityNameError) as e:
        AppType.get_names_from_ids(["app1", "app2"])
    assert "Unable to find app names" in str(e)


def test_validate_id(mock_app_lookup):
    mock_app_lookup({"mod1/app1": "App 1"})
    assert AppType.validate_id("mod1/app1")
    assert AppType.validate_id("mod1.app1")
    assert AppType.validate_id("not_an_app") is False


def test_validate_id_fail(mock_network_error):
    assert AppType.validate_id("Some_app") is False
