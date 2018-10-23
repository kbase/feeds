from ..base import TimelineStorage
# from .connection import get_mongo_connection


class MongoTimelineStorage(TimelineStorage):
    def add_to_timeline(self, activity):
        raise NotImplementedError()

    def get_timeline(self):
        raise NotImplementedError()

    def remove_from_timeline(self, activity_ids):
        raise NotImplementedError()
