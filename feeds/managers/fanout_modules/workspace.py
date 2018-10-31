from .base import FanoutModule
from feeds.biokbase.workspace.client import Workspace

class WorkspaceFanout(FanoutModule):
    def get_target_users(self):
        return self.note.target