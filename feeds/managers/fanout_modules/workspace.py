from .base import FanoutModule
from feeds.biokbase.workspace.client import Workspace
from feeds.config import get_config


class WorkspaceFanout(FanoutModule):
    def get_target_users(self):
        cfg = get_config()
        ws = Workspace(url=cfg.ws_url)

        if self.note.users:
            return self.note.users
        else:
            return self.note.target
