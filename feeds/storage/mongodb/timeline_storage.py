from pymongo import (
    ASCENDING,
    DESCENDING
)
from ..base import TimelineStorage
from .connection import get_feeds_collection


class MongoTimelineStorage(TimelineStorage):
    def add_to_timeline(self, activity):
        raise NotImplementedError()

    def get_timeline(self, count=10, include_seen=False, level=None, verb=None, sort=None):
        """
        :param count: int > 0
        :param include_seen: boolean
        :param level: Level or None
        :param verb: Verb or None
        """
        # TODO: add filtering
        # TODO: input validation
        coll = get_feeds_collection()
        query = {
            "users": [self.user_id]
        }
        if not include_seen:
            query['unseen'] = [self.user_id]
        if level is not None:
            query['level'] = level.id
        if verb is not None:
            query['verb'] = verb.id
        timeline = coll.find(query).sort("created", DESCENDING)
        serial_notes = [note for note in timeline]
        return serial_notes

    def remove_from_timeline(self, activity_ids):
        raise NotImplementedError()
