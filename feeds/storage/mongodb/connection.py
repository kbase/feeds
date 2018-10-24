import pymongo
from pymongo import (
    MongoClient
)
from feeds.config import get_config
import feeds.logger as log

_connection = None

_COL_NOTIFICATIONS = "notifications"
_INDEXES = [
    [("created", pymongo.DESCENDING)]
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
        self.conn = MongoClient(host=self.cfg.db_host, port=self.cfg.db_port)
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
