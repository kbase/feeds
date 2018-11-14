from .base import FanoutModule


class GroupsFanout(FanoutModule):
    def get_target_users(self):

        return list(set(self.note.users + self.note.target))
