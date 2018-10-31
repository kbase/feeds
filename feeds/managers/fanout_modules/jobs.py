from .base import FanoutModule
from feeds.biokbase.NarrativeJobService.Client import NarrativeJobService

class JobsFanout(FanoutModule):
    def get_target_users(self):
        return self.note.target