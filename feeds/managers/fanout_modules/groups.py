from .base import FanoutModule


class GroupsFanout(FanoutModule):
    def get_target_users(self):
        return self.note.target
