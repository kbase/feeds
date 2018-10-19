from .exceptions import MissingLevelError

_level_register = dict()

def register(level):
    if not issubclass(level, Level):
        raise TypeError("Can only register Level subclasses")

    if level.id is None:
        raise ValueError("A level must have an id")
    elif str(level.id) in _level_register:
        raise ValueError("The level id '{}' is already taken by {}".format(level.id, _level_register[str(level.id)].name))

    if level.name is None:
        raise ValueError("A level must have an name form")
    elif level.name.lower() in _level_register:
        raise ValueError("The level '{}' is already registered!".format(level.name))

    _level_register.update({
        str(level.id): level,
        level.name.lower(): level
    })

def get_level(key):
    key = str(key)
    if key.lower() in _level_register:
        return _level_register[key]
    else:
        raise MissingLevelError('Level "{}" not found.'.format(key))

def translate_level(level):
    """
    Allows level to be either an id, a name, or a Level.
    Regardless, returns the Level instance, or raises a MissingLevelError

    :param level: Either a string or a Level. (stringify numerical ids before looking them up)
    """
    if isinstance(level, str):
        return get_level(level)
    elif issubclass(level, level):
        return get_level(level.name)
    else:
        raise TypeError("Must be either a subclass of Level or a string.")


class Level(object):
    id = 0
    name = None

class Alert(Level):
    id = 1
    name = 'alert'

class Warning(Level):
    id = 2
    name = 'warning'

class Error(Level):
    id = 3
    name = 'error'

class Request(Level):
    id = 4
    name = 'request'