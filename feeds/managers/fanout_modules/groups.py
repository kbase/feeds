from .base import FanoutModule


class GroupsFanout(FanoutModule):
    def get_target_users(self):

        if self.note.users:
            return self.note.users
        else:
            return self.note.target
