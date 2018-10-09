from .base import BaseActivity
import uuid

class Notification(BaseActivity):
    def __init__(self, actor, note_type, note_object, target=None, content={}):
        """
        :param actor: user id of the actor (or kbase or global)
        :param note_type: type of note, uses standard activity streams verbs
        :param note_object: object of the note
        :param target: target of the note
        :param content: freeform content of the note
        """
        self.actor = actor
        self.note_type = note_type
        self.object = note_object
        self.target = target
        self.content = content
        self._id = uuid.uuid4()

    @property
    def id(self):
        return self._id

    def serialize(self):
        return