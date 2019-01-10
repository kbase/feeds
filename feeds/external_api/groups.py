from ..config import get_config
import requests
from typing import (
    List,
    Dict
)
from feeds.exceptions import GroupsError

config = get_config()
GROUPS_URL = config.groups_url

Response = requests.models.Response


def get_groups(user: str) -> list:
    """
    Returns the list of groups that a user belongs to.
    """
    raise NotImplementedError()


def get_group_names(group_ids: List[str]) -> Dict[str, str]:
    """
    Returns a mapping from group id to group names given a list of group ids.
    """
    raise NotImplementedError()


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
            "Error while looking up group id: " +
            res['error'].get('message', 'no message available')
        )


def __groups_request(path: str, token: str=None) -> Response:
    headers = {"Authorization": token}
    r = requests.get(path, headers=headers)
    # the requests that fail based on the token (401, 403) get returned for the
    # calling function to turn into an informative error
    # others - 404, 500 - get raised
    r.raise_for_status()
    return r
