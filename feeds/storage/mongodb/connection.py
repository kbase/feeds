from pymongo import (
    MongoClient,
    ASCENDING,
    DESCENDING
)
from feeds.config import get_config
import feeds.logger as log

_connection = None

_COL_NOTIFICATIONS = "notifications"

# Searches to support:
# 1. Lookup by activity id. Easy.
# 2. Lookup all by user, include docs where user is not in unseen, sort by time.
# 3. Lookup all by user, ignore docs where user is not in unseen, sort by time.
# 4. Lookup all by user, sort by source, then sort by time.
# 5. Lookup all by user, sort by type, then sort by time.
# 6. Lookup all by user, sort by source, then sort by time, then sort by time.
# 7. Aggregations... later. Maybe part of the Timeline class.

_INDEXES = [
    [("act_id", ASCENDING)],

    # sort by creation date
    [("created", DESCENDING)],

    # sort by target users
    [("users", ASCENDING)],

    # sort by unseen users
    [("unseen", ASCENDING)],

    # sort by source, then creation date
    [("users", ASCENDING), ("source", ASCENDING), ("created", DESCENDING)],

    # sort by level, then creation date
    [("users", ASCENDING), ("level", ASCENDING), ("created", DESCENDING)]
]


def get_feeds_collection():
    conn = get_mongo_connection()
    return conn.get_collection(_COL_NOTIFICATIONS)


def get_mongo_connection():
    global _connection
    if _connection is None:
        _connection = FeedsMongoConnection()
    return _connection


class FeedsMongoConnection(object):
    def __init__(self):
        self.cfg = get_config()
        log.log(__name__, "opening MongoDB connection {} {}".format(
            self.cfg.db_host, self.cfg.db_port)
        )
        self.conn = MongoClient(
            host=self.cfg.db_host,
            port=self.cfg.db_port,
            username=self.cfg.db_user,
            password=self.cfg.db_pw)
        self.db = self.conn[self.cfg.db_name]
        self._setup_indexes()
        self._setup_schema()

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def _setup_indexes(self):
        coll = self.get_collection(_COL_NOTIFICATIONS)
        for index in _INDEXES:
            coll.create_index(index)

    def _setup_schema(self):
        pass
