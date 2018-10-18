from .base import BaseActivity
import uuid
import json
from datetime import datetime
from ..util import epoch_ms
from .. import verbs

class Notification(BaseActivity):
    def __init__(self, actor, verb, note_object, source, target=None, context={}):
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

        TODO:
            * decide on global ids for admin use
            * validate actor = real kbase id (or special)
            * validate type is valid
            * validate object is valid
            * validate target is valid
            * validate context fits
        """
        self.actor = actor
        self.verb = verbs.translate_verb(verb)
        self.object = note_object
        self.source = source
        self.target = target
        self.context = context
        self.time = epoch_ms()  # int timestamp down to millisecond

    def _validate(self):
        """
        Validates whether the notification fields are accurate. Should be called before sending a new notification to storage.
        """
        self.validate_actor(self.actor)

    def validate_actor(self):
        """
        TODO: add group validation. only users are actors for now.
        TODO: migrate to base class for users
        """
        pass