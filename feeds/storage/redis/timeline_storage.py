from ..base import TimelineStorage
from .connection import get_redis_connection
from feeds.config import get_config
from .util import (
    get_user_key,
    get_note_id
)

class RedisTimelineStorage(TimelineStorage):
    # TODO: CACHING!!

    def __init__(self, user_id):
        self.user_id = user_id

    def get_timeline(self, count):
        """
        Gets the user's timeline of activity ids.
        """
        r = get_redis_connection()
        user_key = get_user_key(self.user_id)
        user_timeline = r.zrevrange(user_key, 0, count)
        return user_timeline

    def add_to_timeline(self, note):
        r = get_redis_connection()
        feed_key = get_user_key(self.user_id)
        r.zadd(feed_key, note.time, get_note_id(note))

    def remove_from_timeline(self, note):
        raise NotImplementedError()