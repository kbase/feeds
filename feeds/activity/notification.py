from .base import BaseActivity

class Notification(BaseActivity):
    def __init__(self, actor, note_type, note_object, target=None, content={}):
        self.actor = actor
        self.note_type = note_type
        self.object = note_object
        self.target = target
        self.content = content

    @property
    def serialization_id(self):


    def serialize(self):
        return