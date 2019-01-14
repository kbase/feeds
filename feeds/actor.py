"""
A module for defining actors.
TODO: decide whether to use a class, or just a validated string. I'm leaning toward string.
"""
from .external_api.auth import (
    validate_user_id,
    validate_user_ids
)
from .external_api.groups import (
    validate_group_id
)
from .exceptions import InvalidActorError


def validate_actor(actor, actor_type="user"):
    if actor_type == "user":
        if validate_user_id(actor):
            return True
        else:
            raise InvalidActorError("Actor '{}' is not a real user.".format(actor))
    elif actor_type == "group":
        if validate_group_id(actor):
            return True
        else:
            raise InvalidActorError("Actor '{}' is not a real group.".format(actor))


def actor_ids_to_names(id_list: list):
    """
    Determines which ids are users vs groups, validates them separately.
    12/19/2018 - assumes all are users right now.
    TODO - add groups lookup when that endpoint exists.
    :param list id_list: list of user/group ids to fetch the full name for
    :return: a dictionary mapping from id to type and real name
        keys = ids given in id_list
        values = a dict with "name" = the real name and "type" = either "user" or "group"
        if any keys do not match, their value is None
    :rtype: dict
    :raises HTTPError: if anything goes wrong with the lookup
    """
    user_ids = validate_user_ids(id_list)
    ret = dict()
    for u in user_ids:
        ret[u] = None
        if user_ids[u] is not None:
            ret[u] = {"type": "user", "name": user_ids[u]}
    return ret
