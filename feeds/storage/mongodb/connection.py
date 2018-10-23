from pymongo import MongoClient
from feeds.config import get_config

_connection = None


def get_mongo_connection():
    global _connection
    if _connection is None:
        _connection = _build_mongo_connection()
    return _connection


def _build_mongo_connection():
    cfg = get_config()
    new_conn = MongoClient(host=cfg.db_host, port=cfg.db_port)
    # TODO: other indexing and config stuff goes here as needed.
    return new_conn
