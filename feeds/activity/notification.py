from .base import BaseActivity
import uuid
import json
from ..util import epoch_ms
from .. import verbs
from .. import notification_level
from feeds.exceptions import (
    InvalidExpirationError,
    InvalidNotificationError
)
import datetime
from feeds.config import get_config
from feeds.entity.entity import Entity
from typing import (
    List,
    TypeVar
)
N = TypeVar('N', bound='Notification')


class Notification(BaseActivity):
    def __init__(self, actor: Entity, verb: str, note_object: Entity, source: str,
                 level='alert', target: List[Entity]=[], context: dict={},
                 expires: int=None, external_key: str=None, seen: bool=False,
                 users: List[Entity]=[]):
        """
        A notification is roughly of this form:
            actor, verb, object, target
        for example, If I share a narrative (workspace) with another user, that
        would be the overall activity:
            wjriehl shared narrative XYZ with you.
        or, broken down:
            actor: wjriehl
            verb: share
            object: narrative xyz
            target: you (another user)

        :param actor: user id of the actor (or 'kbase').
        :param verb: type of note, uses standard activity streams verbs, plus some others.
            This is either a string or a Verb. A MissingVerbError will be raised if it's a string
            and not in the list.
        :param note_object: object of the note. Should be a string. Examples:
            a Narrative name
            a workspace id
            a group name
        :param source: source service for the note. String.
        :param actor_name: Real name of the actor (or None)
        :param level: The level of the notification. Allowed values are alert, warning, request,
            error (default "alert")
        :param target: target of the note. Optional. Should be a user id or group id if present.
        :param context: freeform context of the note. key-value pairs.
        :param validate: if True, runs _validate immediately
        :param expires: if not None, set a new expiration date - should be an int, ms since epoch
        :param external_key: an optional special key given by the service that created the
            notification
        :param seen: if True, then this Notification has been seen before. This will be
            context-dependent, based on who is requesting this Notification.

        TODO:
            * decide on global ids for admin use
            * validate actor = real kbase id (or special)
            * validate type is valid
            * validate object is valid
            * validate target is valid
            * validate context fits
        """
        assert actor is not None, "actor must not be None"
        assert verb is not None, "verb must not be None"
        assert note_object is not None, "note_object must not be None"
        assert source is not None, "source must not be None"
        assert level is not None, "level must not be None"
        assert target is None or isinstance(target, list), "target must be either a list or None"
        assert users is None or isinstance(users, list), "users must be either a list or None"
        assert context is None or isinstance(context, dict), "context must be either a dict or None"

        self.id = str(uuid.uuid4())
        self.actor = actor
        self.verb = verbs.translate_verb(verb)
        self.object = note_object
        self.source = source
        self.target = target
        self.context = context
        self.level = notification_level.translate_level(level)
        self.created = epoch_ms()  # int timestamp down to millisecond
        if expires is None:
            expires = self._default_lifespan() + self.created
        self.validate_expiration(expires, self.created)
        self.expires = expires
        self.external_key = external_key
        self.seen = seen
        self.users = users

    def validate(self) -> None:
        """
        Validates whether the notification fields are accurate. Should be called before
        sending a new notification to storage.
        Raises exceptions if invalid. Currently just raises an InvalidExpirationError, as
        that's all it checks...
        """
        self.validate_expiration(self.expires, self.created)
        # TODO: do this later if we need to
        # validate_actor(self.actor)

    def validate_expiration(self, expires: int, created: int):
        """
        Validates whether the expiration time is valid and after the created time.
        If yes, returns True. If not, raises an InvalidExpirationError.
        """
        # Just validate that the time looks like a real time in epoch millis.
        try:
            datetime.datetime.fromtimestamp(expires/1000)
        except (TypeError, ValueError):
            raise InvalidExpirationError(
                "Expiration time should be the number "
                "of milliseconds since the epoch"
            )
        if expires <= created:
            raise InvalidExpirationError(
                "Notifications should expire sometime after they are created"
            )

    def _default_lifespan(self) -> int:
        """
        Returns the default lifespan of this notification in ms.
        """
        return get_config().lifespan * 24 * 60 * 60 * 1000

    def to_dict(self) -> dict:
        """
        Returns a dict form of the Notification.
        Useful for storing in a document store, returns the id of each verb and level.
        Less useful, but not terrible, for returning to a user.
        exceptions:
        * seen is a transient state and isn't included.
        * actor_name is managed by the auth service, and might change, so isn't included
        """
        dict_form = {
            "id": self.id,
            "actor": self.actor.to_dict(),
            "verb": self.verb.id,
            "object": self.object.to_dict(),
            "source": self.source,
            "context": self.context,
            "level": self.level.id,
            "created": self.created,
            "expires": self.expires,
            "external_key": self.external_key,
        }
        target_dict = []
        if self.target is not None:
            target_dict = [t.to_dict() for t in self.target]
            dict_form["target"] = target_dict
        user_dict = []
        if self.users is not None:
            user_dict = [u.to_dict() for u in self.users]
            dict_form["users"] = user_dict

        return dict_form

    def user_view(self) -> dict:
        """
        Returns a view of the Notification that's intended for the user.
        That means we leave out the users and external keys.
        """
        view = {
            "id": self.id,
            "actor": self.actor.to_dict(with_name=True),
            "verb": self.verb.past_tense,
            "object": self.object.to_dict(with_name=True),
            "source": self.source,
            "context": self.context,
            "target": self.target,
            "level": self.level.name,
            "created": self.created,
            "expires": self.expires,
            "seen": self.seen
        }
        if self.external_key is not None:
            view["external_key"] = self.external_key
        target_dict = []
        if self.target is not None:
            target_dict = [t.to_dict(with_name=True) for t in self.target]
            view["target"] = target_dict
        return view

    def serialize(self) -> str:
        """
        Serializes this notification to a string for caching / simple storage (e.g. Redis).
        Assumes it's been validated.
        Just dumps it all to a json string.
        """
        serial = {
            "i": self.id,
            "a": str(self.actor),
            "v": self.verb.id,
            "o": str(self.object),
            "s": self.source,
            "t": [str(t) for t in self.target],
            "l": self.level.id,
            "c": self.created,
            "e": self.expires,
            "x": self.external_key,
            "n": self.context,
            "u": [str(u) for u in self.users]
        }
        return json.dumps(serial, separators=(',', ':'))

    @classmethod
    def deserialize(cls, serial: str, token: str=None) -> N:
        """
        Deserializes and returns a new Notification instance.
        """
        try:
            assert serial
        except AssertionError:
            raise InvalidNotificationError("Can't deserialize an input of 'None'")
        try:
            struct = json.loads(serial)
        except json.JSONDecodeError:
            raise InvalidNotificationError("Can only deserialize a JSON string")
        required_keys = set(['a', 'v', 'o', 's', 'l', 't', 'c', 'i', 'e'])
        missing_keys = required_keys.difference(struct.keys())
        if missing_keys:
            raise InvalidNotificationError('Missing keys: {}'.format(missing_keys))
        users = [Entity.from_str(u, token=token) for u in struct.get('u', [])]
        target = [Entity.from_str(t, token=token) for t in struct.get('t', [])]
        deserial = cls(
            Entity.from_str(struct['a'], token=token),
            str(struct['v']),
            Entity.from_str(struct['o'], token=token),
            struct['s'],
            level=str(struct['l']),
            target=target,
            context=struct.get('n'),
            external_key=struct.get('x'),
            users=users
        )
        deserial.created = struct['c']
        deserial.id = struct['i']
        deserial.expires = struct['e']
        return deserial

    @classmethod
    def from_dict(cls, serial: dict, token: str=None) -> N:
        """
        Returns a new Notification from a serialized dictionary (e.g. used in Mongo)
        """
        try:
            assert serial is not None and isinstance(serial, dict)
        except AssertionError:
            raise InvalidNotificationError("Can only run 'from_dict' on a dict.")
        required_keys = set([
            'actor', 'verb', 'object', 'source', 'level', 'created', 'expires', 'id'
        ])
        missing_keys = required_keys.difference(set(serial.keys()))
        if missing_keys:
            raise InvalidNotificationError('Missing keys: {}'.format(missing_keys))
        deserial = cls(
            Entity.from_dict(serial['actor'], token=token),
            str(serial['verb']),
            Entity.from_dict(serial['object'], token=token),
            serial['source'],
            level=str(serial['level']),
            target=[Entity.from_dict(t, token=token) for t in serial.get('target', [])],
            context=serial.get('context'),
            external_key=serial.get('external_key'),
            seen=serial.get('seen', False),
            users=[Entity.from_dict(u, token=token) for u in serial.get('users', [])]
        )
        deserial.created = serial['created']
        deserial.expires = serial['expires']
        deserial.id = serial['id']
        return deserial

    @staticmethod
    def update_entity_names(notes: List[N], token: str=None) -> None:
        entities = list()
        for n in notes:
            entities.append(n.actor)
            entities.append(n.object)
            entities = entities + n.target
            entities = entities + n.users
        Entity.fetch_entity_names(entities, token)
