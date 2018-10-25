from .exceptions import MissingVerbError

_verb_register = dict()


def register(verb):
    if not issubclass(verb, Verb):
        raise TypeError("Can only register Verb subclasses")

    if verb.id is None:
        raise ValueError("A verb must have an id")
    elif str(verb.id) in _verb_register:
        raise ValueError("The verb id '{}' is already taken by {}".format(
            verb.id, _verb_register[str(verb.id)].infinitive))

    if verb.infinitive is None:
        raise ValueError("A verb must have an infinitive form")
    elif verb.infinitive.lower() in _verb_register:
        raise ValueError("The verb '{}' is already registered!".format(verb.infinitive))

    if verb.past_tense is None:
        raise ValueError("A verb must have a past tense form")
    elif verb.past_tense.lower() in _verb_register:
        raise ValueError("The verb '{}' is already registered!".format(verb.past_tense))

    _verb_register.update({
        str(verb.id): verb,
        verb.infinitive.lower(): verb,
        verb.past_tense.lower(): verb
    })


def translate_verb(verb):
    """
    Translates a given verb into a verb object.
    4 cases -
        - if it's a string, return get_verb (let the MissingVerbError rise)
        - if it's a verb, but not registered, raise a MissingVerbError
        - if it's a verb that's registered, return it
        - if it's not a Verb or a str, raise a TypeError
    """
    if isinstance(verb, int):
        return get_verb(str(verb))
    elif isinstance(verb, str):
        return get_verb(verb)
    elif isinstance(verb, Verb):
        return get_verb(verb.infinitive)
    else:
        raise TypeError("Must be either a subclass of Verb or a string.")


def get_verb(key):
    # if they're both None, fail.
    # otherwise, look it up.
    assert key is not None

    key = str(key)
    if key.lower() in _verb_register:
        return _verb_register[key]()
    else:
        raise MissingVerbError('Verb "{}" not found.'.format(key))


class Verb(object):
    id = None
    infinitive = None
    past_tense = None

    def __str__(self):
        return self.infinitive

    def serialize(self):
        return self.id


class Invite(Verb):
    id = 1
    infinitive = "invite"
    past_tense = "invited"


class Accept(Verb):
    id = 2
    infinitive = "accept"
    past_tense = "accepted"


class Reject(Verb):
    id = 3
    infinitive = "reject"
    past_tense = "rejected"


class Share(Verb):
    id = 4
    infinitive = "share"
    past_tense = "shared"


class Unshare(Verb):
    id = 5
    infinitive = "unshare"
    past_tense = "unshared"


class Join(Verb):
    id = 6
    infinitive = "join"
    past_tense = "joined"


class Leave(Verb):
    id = 7
    infinitive = "leave"
    past_tense = "left"


class Request(Verb):
    id = 8
    infinitive = "request"
    past_tense = "requested"


class Update(Verb):
    id = 9
    infinitive = "update"
    past_tense = "updated"


register(Invite)
register(Accept)
register(Reject)
register(Share)
register(Unshare)
register(Join)
register(Leave)
register(Request)
register(Update)
