import pytest
from feeds.external_api.workspace import (
    validate_narrative_id,
    validate_workspace_id,
    validate_workspace_ids,
    get_workspace_name,
    get_workspace_names,
    get_narrative_name,
    get_narrative_names
)
from feeds.exceptions import WorkspaceError

DUMMY_WS_INFO = [1, "some_name"]
DUMMY_WS_INFO2 = [2, "some_other_name"]
DUMMY_NARR_INFO = [1, "some_name", "some_owner", "timestamp", 5, "a", "n", "unlocked", {"narrative_nice_name": "Foo", "narrative": 1}]
DUMMY_NARR_INFO2 = [2, "some_other_name", "some_owner", "timestamp", 6, "a", "n", "unlocked", {"narrative_nice_name": "Bar", "narrative": 2}]
DUMMY_NARR_INFO_NO_NAME = [3, "some_name", "some_owner", "timestamp", 5, "a", "n", "unlocked", {"narrative": 1}]

def test_validate_narr_id(mock_workspace_info):
    mock_workspace_info(DUMMY_NARR_INFO)
    assert validate_workspace_id(1)

def test_validate_narr_id_fail(mock_workspace_info_invalid):
    mock_workspace_info_invalid(1)
    assert validate_workspace_id(1) is False

def test_validate_narr_id_err(mock_workspace_info_error):
    mock_workspace_info_error(1)
    assert validate_workspace_id(1) is False

def test_validate_ws_id(mock_workspace_info):
    mock_workspace_info(DUMMY_WS_INFO)
    assert validate_workspace_id(1)

def test_validate_ws_id_fail(mock_workspace_info_invalid):
    mock_workspace_info_invalid(1)
    assert validate_workspace_id(1) is False

def test_validate_ws_id_err(mock_workspace_info_error):
    mock_workspace_info_error(1)
    assert validate_workspace_id(1) is False

def test_validate_ws_ids(mock_workspace_info):
    mock_workspace_info(DUMMY_WS_INFO)
    valids = validate_workspace_ids([1, 2])
    std = {1: True, 2: False}
    for i in [1, 2]:
        assert valids.get(i) == std[i]

def test_validate_ws_ids_fail(mock_workspace_info_invalid):
    mock_workspace_info_invalid(1)
    valids = validate_workspace_ids([1])
    assert valids[1] is False

def test_validate_ws_ids_err(mock_workspace_info_error):
    mock_workspace_info_error(1)
    valids = validate_workspace_ids([1])
    assert valids[1] is None

def test_get_ws_name(mock_workspace_info):
    mock_workspace_info(DUMMY_WS_INFO)
    assert get_workspace_name(DUMMY_WS_INFO[0]) == DUMMY_WS_INFO[1]

def test_get_ws_name_fail(mock_workspace_info_invalid):
    mock_workspace_info_invalid(DUMMY_WS_INFO[0])
    assert get_workspace_name(DUMMY_WS_INFO[0]) is None

def test_get_ws_name_err(mock_workspace_info_error):
    mock_workspace_info_error(DUMMY_WS_INFO[0])
    with pytest.raises(WorkspaceError) as e:
        get_workspace_name(DUMMY_WS_INFO[0])
    assert "Unable to find name for workspace id: {}".format(DUMMY_WS_INFO[0]) in str(e)

def test_get_ws_names(mock_workspace_info):
    pass

def test_get_ws_names_fail(mock_workspace_info_invalid):
    pass

def test_get_ws_names_err(mock_workspace_info_error):
    pass

def test_get_narr_name(mock_workspace_info):
    mock_workspace_info(DUMMY_NARR_INFO)
    assert get_narrative_name(DUMMY_NARR_INFO[0]) == DUMMY_NARR_INFO[8]["narrative_nice_name"]
    mock_workspace_info(DUMMY_NARR_INFO_NO_NAME)
    assert get_narrative_name(DUMMY_NARR_INFO_NO_NAME[0]) == "Untitled"

def test_get_narr_name_fail(mock_workspace_info_invalid):
    mock_workspace_info_invalid(DUMMY_NARR_INFO[0])
    assert get_narrative_name(DUMMY_NARR_INFO[0]) is None

def test_get_narr_name_err(mock_workspace_info_error):
    mock_workspace_info_error(DUMMY_NARR_INFO[0])
    with pytest.raises(WorkspaceError) as e:
        get_narrative_name(DUMMY_NARR_INFO[0])
    assert "Unable to find name for narrative id: {}".format(DUMMY_NARR_INFO[0]) in str(e)

def test_get_narr_names(mock_workspace_info):
    pass

def test_get_narr_names_fail(mock_workspace_info_invalid):
    pass

def test_get_narr_names_err(mock_workspace_info_error):
    pass

