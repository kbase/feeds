from abc import abstractmethod
from feeds.activity.notification import Notification


class FanoutModule(object):
    """
    Base module.
    Defines interface for how a Manager should fan out activities based on the activity
    source.
    """
    def __init__(self, note: Notification):
        self.note = note

    @abstractmethod
    def get_target_users(self):
        pass
