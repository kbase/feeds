from .base import BaseActivity
import uuid
import json
from datetime import datetime
from ..util import epoch_ms
from .. import verbs

class Notification(BaseActivity):
    def __init__(self, actor, verb, note_object, target=None, context={}):
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

        :param actor: user id of the actor (or kbase or global)
        :param verb: type of note, uses standard activity streams verbs, plus some others. This is either a string or a Verb.
        :param note_object: object of the note
        :param target: target of the note
        :param context: freeform context of the note

        TODO:
            * validate actor = real kbase id (or special)
            * validate type is valid
            * validate object is valid
            * validate target is valid
            * validate context fits
        """
        self.actor = actor
        self.verb = verb
        self.object = note_object
        self.target = target
        self.context = context
        self.time = epoch_ms()  # int timestamp down to millisecond

    def serialize_transport(self):
        """
        Returns a dict form of this for transport (maybe some __ function?)
        """
        return {
            "id": self._id,
            "actor": self.actor,
            "type": self.verb,
            "object": self.object,
            "target": self.target,
            "context": self.context
        }
