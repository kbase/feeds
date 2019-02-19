from ..base import ActivityStorage
from .connection import get_redis_connection
# from cachetools import TTLCache
from .util import get_activity_key
from collections import defaultdict

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

# activity_cache = TTLCache(1000, 600)


class RedisActivityStorage(ActivityStorage):
    def serialize(self):
        raise NotImplementedError()

    def deserialize(self):
        raise NotImplementedError()

    def add_to_storage(self, activity):
        # namespaces notes under the first character of their id.
        # should help with sharding, if we need to.
        key = get_activity_key(activity)
        r = get_redis_connection()
        r.hset(key, activity.id, activity.serialize())

    def get_from_storage(self, activity_ids):
        # returns a list of serialized strings. We don't know what subclass
        # to return as here, so it's up to the calling Manager or Feed to deserialize.

        # first, map the activity_ids onto their stored hash keys
        lookup_map = defaultdict(list)
        for id_ in activity_ids:
            lookup_map[get_activity_key(id_)].append(id_)
        r = get_redis_connection()
        acts = dict()  # act id -> Activity
        for key in lookup_map:
            id_list = lookup_map[key]
            serial_acts = r.hmget(key, lookup_map[key])
            # The above are the same length (redis fills in None for missing keys)
            # just smash them into a dict
            for idx, id_ in enumerate(id_list):
                acts[id_] = serial_acts[idx]
        # now, just map the acts dict back onto the original activity_ids list
        # to maintain the order
        ret_list = list()
        for id_ in activity_ids:
            ret_list.append(acts[id_])
        return ret_list

    def remove_from_storage(self, activity_ids):
        raise NotImplementedError()
