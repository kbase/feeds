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


def validate_narrative_id(ws_id: Union[int, str], token: str) -> bool:
    """
    Returns True if the workspace id exists and has a narrative registered in it, False otherwise.
    Raises a WorkspaceError if it can't be reached for
    """
    try:
        info = __ws_client(token).get_workspace_info({"id": ws_id})
        return info[8].get("narrative") is not None
    except ServerError:
        # It'll be because we can't see it, or it's deleted, or that ws doesn't exist.
        # Either way, that's negative.
        return False


def validate_workspace_id(ws_id: Union[int, str], token: str) -> bool:
    """
    Returns True if the workspace id exists, False otherwise.
    """
    try:
        __ws_client(token).get_workspace_info({"id": ws_id})
        return True
    except ServerError as e:
        if "Anonymous users may not read workspace" in e.message:
            return True
        else:
            return False


def validate_workspace_ids(ws_ids: List[Union[int, str]], token: str) -> Dict[str, bool]:
    """
    For a bunch of workspaces, this will return a dictionary where each key is the workspace id,
    and each value is either True if it exists, False if it doesn't, and a ServerError if an
    error occurred while trying to validate.
    """
    ws = __ws_client(token)
    ids = {}
    for ws_id in ws_ids:
        try:
            info = ws.get_workspace_info({"id": ws_id})
            ids[ws_id] = str(info[0]) == str(ws_id)   # dumb, but helps with testing
        except ServerError as e:
            if "No workspace with id" in e.message:
                ids[ws_id] = False
            else:
                ids[ws_id] = None
    return ids


def get_workspace_name(ws_id: int, token: str) -> str:
    try:
        info = __ws_client(token).get_workspace_info({"id": ws_id})
        return info[1]
    except ServerError as e:
        if "No workspace with id" in e.message:
            return None
        raise WorkspaceError(
            "Unable to find name for workspace id: {}: {}".format(ws_id, e.message)
        )


def get_workspace_names(ws_ids: List[Union[int, str]], token: str) -> Dict[str, str]:
    ws = __ws_client(token)
    names = dict()
    for ws_id in ws_ids:
        try:
            info = ws.get_workspace_info({"id": ws_id})
            names[ws_id] = info[1]
        except ServerError:
            names[ws_id] = None
    return names


def get_narrative_name(ws_id: int, token: str) -> str:
    try:
        info = __ws_client(token).get_workspace_info({"id": ws_id})
        if info[8] is not None and isinstance(info[8], dict):
            meta = info[8]
            if 'narrative_nice_name' in meta:
                return meta['narrative_nice_name']
            elif 'narrative' in meta:
                return 'Untitled'
            else:
                raise WorkspaceError(
                    "Unable to find name for narrative id: {}: info not found.".format(ws_id)
                )
    except ServerError as e:
        if "No workspace with id" in e.message:
            return None
        raise WorkspaceError(
            "Unable to find name for narrative id: {}: {}".format(ws_id, e.message)
        )


def get_narrative_names(ws_ids: List[Union[int, str]], token: str) -> Dict[str, str]:
    ws = __ws_client(token)
    names = dict()
    for ws_id in ws_ids:
        try:
            info = ws.get_workspace_info({"id": ws_id})
            meta = info[8]
            if 'narrative_nice_name' in meta:
                names[ws_id] = meta['narrative_nice_name']
            elif 'narrative' in meta:
                names[ws_id] = 'Untitled'
            else:
                names[ws_id] = None
        except ServerError:
            names[ws_id] = None
    return names


def __ws_client(token: str) -> Workspace:
    if token is None:
        token = config.auth_token
    return Workspace(url=config.ws_url, token=token)
