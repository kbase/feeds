from .base import BaseActivity
import uuid
import json
from ..util import epoch_ms
from .. import verbs
from ..actor import validate_actor
from .. import notification_level
from feeds.exceptions import InvalidExpirationError
import datetime


class Notification(BaseActivity):
    def __init__(self, actor, verb, note_object, source, level='alert', target=None,
                 context={}, expires=None, external_key=None):
        """
        A notification is roughly of this form:
            actor, verb, object, (target)
        (with target optional)
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
        :param target: target of the note. Optional. Should be a user id or group id if present.
        :param context: freeform context of the note. key-value pairs.
        :param validate: if True, runs _validate immediately
        :param expires: if not None, set a new expiration date - should be an int, ms since epoch
        :param external_key: an optional special key given by the service that created the
            notification

        TODO:
            * decide on global ids for admin use
            * validate actor = real kbase id (or special)
            * validate type is valid
            * validate object is valid
            * validate target is valid
            * validate context fits
        """
        self.id = str(uuid.uuid4())
        self.actor = actor
        self.verb = verbs.translate_verb(verb)
        self.object = note_object
        self.source = source
        self.target = target
        self.context = context
        self.level = notification_level.translate_level(level)
        self.created = epoch_ms()  # int timestamp down to millisecond
        if expires is not None:
            self.expires = self._default_expiration()
        else:
            self.validate_expiration(expires)
            self.expires = expires
        self.external_key = external_key

    def validate(self):
        """
        Validates whether the notification fields are accurate. Should be called before
        sending a new notification to storage.
        """
        self.validate_expiration(self.expires, self.created)
        validate_actor(self.actor)

    def validate_expiration(self, expires, created):
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
                "of milliseconds since the epoch."
            )
        pass

    def _default_expiration(self):
        """
        Returns the default expiration time of this notification.
        """
        pass

    def to_dict(self):
        """
        Returns a dict form of the Notification.
        Useful for storing in a document store.
        Less useful, but not terrible, for returning to a user.
        """
        dict_form = {
            "id": self.id,
            "actor": self.actor,
            "verb": self.verb.infinitive,
            "object": self.object,
            "source": self.source,
            "context": self.context,
            "level": self.level.name,
            "created": self.created,
            "expires": self.expires,
            "external_key": self.external_key
        }
        return dict_form

    def user_view(self):
        """
        Returns a view of the Notification that's intended for the user.
        That means we leave out the target and external keys.
        """
        pass

    def serialize(self):
        """
        Serializes this notification for caching / simple storage.
        Assumes it's been validated.
        Just dumps it all to a json string.
        """
        serial = {
            "i": self.id,
            "a": self.actor,
            "v": self.verb.id,
            "o": self.object,
            "s": self.source,
            "t": self.target,
            "l": self.level.id,
            "c": self.created,
            "e": self.expires,
            "x": self.external_key
        }
        return json.dumps(serial, separators=(',', ':'))

    @classmethod
    def deserialize(cls, serial):
        """
        Deserializes and returns a new Notification instance.
        """
        if serial is None:
            return None
        struct = json.loads(serial)
        deserial = cls(
            struct['a'],
            str(struct['v']),
            struct['o'],
            struct['s'],
            level=str(struct['l']),
            target=struct.get('t'),
            context=struct.get('c'),
            external_key=struct.get('x')
        )
        deserial.time = struct['c']
        deserial.id = struct['i']
        deserial.time = struct['e']
        return deserial

    @classmethod
    def from_dict(cls, serial):
        """
        Returns a new Notification from a serialized dictionary (e.g. used in Mongo)
        """
        assert serial
        deserial = cls(
            serial['actor'],
            str(serial['verb']),
            serial['object'],
            serial['source'],
            level=str(serial['level']),
            target=serial.get('target'),
            context=serial.get('context'),
            external_key=serial.get('external_key')
        )
        deserial.time = serial['created']
        deserial.expires = serial['expires']
        deserial.id = serial['act_id']
        return deserial
