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
    # MongoActivityStorage.get_by_id
    # MongoActivityStorage.expire_notifications
    [("id", ASCENDING)],

    # MongoActivityStorage.get_by_id
    [("id", ASCENDING), ("source", ASCENDING)],

    # MongoTimelineStorage.get_single_activity_from_timeline
    [("id", ASCENDING), ("users", ASCENDING)],

    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING)],

    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING), ("expires", ASCENDING)],

    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING), ("source", ASCENDING), ("created", DESCENDING)],

    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING), ("source", ASCENDING), ("expires", ASCENDING), ("created", DESCENDING)],

    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING), ("expires", ASCENDING), ("level", ASCENDING), ("created", DESCENDING)],

    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING), ("level", ASCENDING), ("created", DESCENDING)],

    # MongoTimelineStorage.get_unseen_count
    # MongoTimelineStorage.get_timeline
    [("users", ASCENDING), ("expires", ASCENDING)],

    # MongoTimelineStorage.get_timeline
    [
        ("users", ASCENDING),
        ("expires", ASCENDING),
        ("level", ASCENDING),
        ("created", DESCENDING)
    ],

    # MongoTimelineStorage.get_timeline
    [
        ("users", ASCENDING),
        ("expires", ASCENDING),
        ("level", ASCENDING),
        ("verb", ASCENDING),
        ("created", DESCENDING)
    ],
]

_SPARSE_INDEXES = [
    # MongoActivityStorage.get_by_external_key
    [("external_key", ASCENDING), ("source", ASCENDING)]
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
            password=self.cfg.db_pw,
            retryWrites=self.cfg.db_retrywrites,
            authSource=self.cfg.db_name
        )
        self.db = self.conn[self.cfg.db_name]
        self._setup_indexes()
        self._setup_schema()

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def _setup_indexes(self):
        coll = self.get_collection(_COL_NOTIFICATIONS)
        for index in _INDEXES:
            coll.create_index(index)
        for index in _SPARSE_INDEXES:
            coll.create_index(index, sparse=True)

    def _setup_schema(self):
        pass
