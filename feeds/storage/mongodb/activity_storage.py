from ..base import ActivityStorage
from .connection import get_mongo_connection


class MongoActivityStorage(ActivityStorage):
    def add_to_storage(self, activity):
        mongo = get_mongo_connection()
        mongo.do_stuff

    def get_from_storage(self, activity_ids):
        raise NotImplementedError()

    def remove_from_storage(self, activity_ids):
        raise NotImplementedError()
