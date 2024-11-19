from ..config import get_config
import requests
from typing import (
    List,
    Dict
)
from feeds.exceptions import GroupsError
from requests import HTTPError

config = get_config()
GROUPS_URL = config.groups_url

Response = requests.models.Response


def get_user_groups(user_token: str) -> list:
    """
    Returns the list of groups that a user belongs to.
    These are returned as a list of dicts, each of which has an "id" and "name"
    key, representing the group id and name respectively. What else would they be?
    """
    r = __groups_request("/member/", user_token)
    return r.json()


def get_group_names(group_ids: List[str], auth_token: str) -> Dict[str, str]:
    """
    Returns a mapping from group id to group names given a list of group ids.
    """
    # TODO
    group_id_params = ",".join(group_ids)
    r = __groups_request("/names/" + group_id_params, auth_token)
    data = r.json()
    names = dict()
    for n in data:
        names[n["id"]] = n["name"]
    for g_id in group_ids:
        if g_id not in names:
            names[g_id] = None
    return names


def validate_group_id(group_id: str) -> bool:
    """
    Returns True or False if the group id is real or not.
    """
    r = __groups_request("/group/{}/exists".format(group_id))
    res = r.json()
    if 'exists' in res:
        return res['exists']
    elif 'error' in res:
        raise GroupsError(
            f"Error while looking up group id: "
            f"{res['error'].get('message', 'no message available')}"
        )


def __groups_request(path: str, token: str=None) -> Response:
    headers = {"Authorization": token}
    try:
        r = requests.get(GROUPS_URL + path, headers=headers)
        r.raise_for_status()
        return r
    except HTTPError as e:
        raise GroupsError("Unable to fetch group information: {}".format(str(e)))
