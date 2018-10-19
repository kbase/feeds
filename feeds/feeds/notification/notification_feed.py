from ..base import BaseFeed
from feeds.activity.notification import Notification
from feeds.storage.redis.activity_storage import RedisActivityStorage
from feeds.storage.redis.timeline_storage import RedisTimelineStorage
from cachetools import TTLCache
import logging

class NotificationFeed(BaseFeed):
    def __init__(self, user_id):
        self.user_id = user_id
        self.timeline_storage = RedisTimelineStorage(self.user_id)
        self.activity_storage = RedisActivityStorage()
        self.timeline = None
        self.cache = TTLCache(1000, 600)

    def _update_timeline(self):
        """
        Updates a local user timeline cache. This is a list of activity ids
        that are used for fetching from activity storage (for now). Sorted
        by newest first.

        TODO: add metadata to timeline storage - type and verb, first.
        """
        logging.getLogger(__name__).info('Fetching timeline for ' + self.user_id)
        self.timeline = self.timeline_storage.get_timeline()

    def get_notifications(self, count=10):
        return self.get_activities(count=count)

    def get_activities(self, count=10):
        """
        Returns a selection of activities.
        :param count: Maximum number of Notifications to return (default 10)
        """
        # steps.
        # 0. If in cache, return them.  <-- later
        # 1. Get storage adapter.
        # 2. Query it for recent activities from this user.
        # 3. Cache them here.
        # 4. Return them.
        if count < 1 or not isinstance(count, int):
            raise ValueError('Count must be an integer > 0')
        self._update_timeline()
        note_ids = self.timeline
        serial_notes = self.activity_storage.get_from_storage(note_ids)
        note_list = [Notification.deserialize(note) for note in serial_notes]
        return note_list

    def mark_activities(self, activity_ids, seen=False):
        """
        Marks the given list of activities as either seen (True) or unseen (False).
        """
        pass

    def add_notification(self, note):
        return self.add_activity(note)

    def add_activity(self, note):
        """
        Adds an activity to this user's feed
        """
        self.timeline_storage.add_to_timeline(note)

    def add_activities(self):
        """
        Adds several activities to this user's feed.
        """
        pass

