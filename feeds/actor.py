"""
A module for defining actors.
TODO: decide whether to use a class, or just a validated string. I'm leaning toward string.
"""
from .auth import validate_user_id
from .exceptions import InvalidActorError


def validate_actor(actor):
    """
    TODO: groups can be actors, too, when that's ready.
    """
    if validate_user_id(actor):
        return True
    else:
        raise InvalidActorError("Actor '{}' is not a real user.".format(actor))
