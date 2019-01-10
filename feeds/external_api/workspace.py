from ..config import get_config
from ..exceptions import WorkspaceError
from ..biokbase.workspace.client import Workspace
from ..biokbase.workspace.baseclient import ServerError
from typing import (
    List,
    Dict,
    Union
)

config = get_config()


def validate_workspace_id(ws_id: Union[int, str]) -> bool:
    """
    Returns True if the workspace id exists, False otherwise.
    """
    try:
        __ws_client().get_workspace_info({"id": ws_id})
        return True
    except ServerError as e:
        if "No workspace with id" in e.message:
            return False
        raise WorkspaceError("Unable to validate workspace id {}: {}".format(ws_id, e.message))


def validate_workspace_ids(ws_ids: List[Union[int, str]]) -> Dict[str, str]:
    pass


def get_workspace_name(ws_id: int) -> str:
    try:
        info = __ws_client().get_workspace_info({"id": ws_id})
        return info[1]
    except ServerError as e:
        if "No workspace with id" in e.message:
            return None
        raise WorkspaceError(
            "Unable to get workspace name for id {}: {}".format(ws_id, e.message)
        )


def get_workspace_names(ws_ids: List[Union[int, str]]) -> Dict[str, str]:
    pass


def get_narrative_name(ws_id: int) -> str:
    try:
        info = __ws_client().get_workspace_info({"id": ws_id})
        if info[8] is not None and isinstance(info[8], dict):
            meta = info[8]
            if 'narrative_nice_name' in meta:
                return meta['narrative_nice_name']
            elif 'narrative' in meta:
                return 'Untitled'
            else:
                raise WorkspaceError(
                    "Unable to get narrative name for id {}: info not found.".format(ws_id)
                )
    except ServerError as e:
        if "No workspace with id" in e.message:
            return None
        raise WorkspaceError(
            "Unable to get narrative name for id {}: {}".format(ws_id, e.message)
        )


def get_narrative_names(ws_id: List[Union[int, str]]) -> Dict[str, str]:
    pass


def __ws_client() -> Workspace:
    return Workspace(url=config.ws_url, token=config.auth_token)
