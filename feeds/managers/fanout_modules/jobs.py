from .base import FanoutModule
from feeds.biokbase.NarrativeJobService.Client import NarrativeJobService
from feeds.config import get_config


class JobsFanout(FanoutModule):
    def get_target_users(self):
        cfg = get_config()
        njs = NarrativeJobService(url=cfg.njs_url)
        return list(set(self.note.users + self.note.target))
