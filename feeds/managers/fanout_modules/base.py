from abc import abstractmethod
from feeds.activity.notification import Notification
from feeds.entity.entity import Entity
from typing import List


class FanoutModule(object):
    """
    Base module.
    Defines interface for how a Manager should fan out activities based on the activity
    source.
    """
    def __init__(self, note: Notification):
        self.note = note

    @abstractmethod
    def get_target_users(self) -> List[Entity]:
        """
        This should always return a list of Entities, even an empty one.
        Ideally, it'll be a list of users that should see the notification.
        """
        pass
