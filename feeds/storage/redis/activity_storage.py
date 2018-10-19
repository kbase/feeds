from ..base import ActivityStorage
from .connection import get_redis_connection
from cachetools import TTLCache

"""
Activities get added to Redis like this:
Each activity comes from a source - that source is used as the key.
Each activity gets a unique id that it knows how to make.
Each activity can also be serialized/deserialized into a string. Maybe it gets pickled.
So now we have the makings of a hash.
Each key = activity's unique id.
Each value = serialized version of activity.

Should be small and fast.

If we make a MongoDB adapter, it can work with documents.
"""

activity_cache = TTLCache(1000, 600)

class RedisActivityStorage(ActivityStorage):
    def serialize(self):
        raise NotImplementedError()

    def deserialize(self):
        raise NotImplementedError()

    def add_to_storage(self, activity):
        # each source gets its own key
        key = 'notes:{}'.format(activity.source)
        r = get_redis_connection()
        act_key = "{}-{}".format(activity.source, activity.id)
        r.hset(key, activity.id, activity.serialize())

    def get_from_storage(self, activity_ids, source):
        # returns the serialized form, as a list of strings.
        key = 'notes:{}'.format(source)
        r = get_redis_connection()
        return r.hmget(key, activity_ids)

    def remove_from_storage(self, activity_ids):
        raise NotImplementedError()

