"""
A NotificationManager manages adding new notifications.
This is separate from a feed - notifications get added by the KBase system to
user feeds, based on the content and context of the Notification.

See also the docs in NotificationFeed.
"""

from .base import BaseManager
from ..storage.redis.activity_storage import RedisActivityStorage
from ..feeds.notification.notification_feed import NotificationFeed
from feeds.config import get_config


class NotificationManager(BaseManager):
    def __init__(self):
        # init storage
        pass

    def add_notification(self, note):
        """
        Adds a new notification.
        Triggers validation first.
        """
        note.validate()  # any errors get raised to be caught by the server.
        target_users = self.get_target_users(note)
        # add the notification to the database.
        activity_storage = RedisActivityStorage()
        activity_storage.add_to_storage(note)
        for user in target_users:
            # add the notification to the appropriate users' feeds.
            feed = NotificationFeed(user)
            feed.add_notification(note)

    def get_target_users(self, note):
        """
        This is gonna get complex.
        The target users are a combination of:
        - the list in note.target
        - workspace admins (if it comes from a workspace)
        - everyone, if it's global - mark as _global_ feed.
        TODO: add adapters, maybe subclass notifications to handle each source?
        """
        user_list = list()
        if note.target:
            user_list = user_list + note.target
        elif note.source == 'kbase':
            user_list.append(get_config().global_feed)
        return user_list
