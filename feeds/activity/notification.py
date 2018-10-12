from .base import BaseActivity
import uuid
import json
from datetime import datetime

class Notification(BaseActivity):
    serialize_token = "|"

    def __init__(self, actor, verb, note_object, target=None, context={}):
        """
        A notification is roughly of this form - actor, verb, object, (target)
        (with target optional)
        for example, If I share a narrative (workspace)

        :param actor: user id of the actor (or kbase or global)
        :param verb: type of note, uses standard activity streams verbs, plus some others
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
        self.time = int(datetime.utcnow().timestamp()*1000)  # int timestamp down to millisecond

    def serialize_storage(self):
        """
        Serializes this notification for storage
        """
        return "{}|{}|{}|{}|{}|{}".format(self._id, self.actor, self.verb, self.object, self.target, json.dumps(self.context))

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

    @classmethod
    def deserialize_storage(cls, storage_str):
        """
        :param storage_str: string
        """
        split_str = storage_str.split('|', 5)
        return cls(*split_str)






