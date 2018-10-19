from ..base import BaseFeed
from feeds.activity.notification import Notification
from feeds.storage.redis.activity_storage import RedisActivityStorage
from feeds.storage.redis.timeline_storage import RedisTimelineStorage
from cachetools import TTLCache

class NotificationFeed(BaseFeed):
    timeline_storage_class = RedisTimelineStorage
    activity_storage_class = RedisActivityStorage

    def __init__(self, user_id):
        self.user_id = user_id
        self.timeline_storage = timeline_storage_class()
        self.activity_storage = activity_storage_class()
        self.timeline = None
        self.cache = TTLCache(1000, 600)

    def _update_timeline(self):
        """
        Updates a local user timeline cache. This is a list of activity ids
        that are used for fetching from activity storage (for now). Sorted
        by newest first.

        TODO: add metadata to timeline storage - type and verb, first.
        """
        self.timeline = self.timeline_storage.get_timeline(self.user_id)

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
        if count < 1 or not isdigit(str(count)):
            raise ValueError('Count must be an integer > 0')
        self._update_timeline()
        self.note_ids = self.timeline[0:count]

        self.activity_storage.get_activities(note_ids)

    def mark_activities(self, activity_ids, seen=False):
        """
        Marks the given list of activities as either seen (True) or unseen (False).
        """
        pass

    def add_activity(self, note):
        """
        Adds an activity to this user's feed
        """
        self.timeline_storage.add_activity(note)

    def add_activities(self):
        """
        Adds several activities to this user's feed.
        """
        pass

