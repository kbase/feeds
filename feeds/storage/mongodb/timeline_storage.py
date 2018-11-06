import pymongo
from ..base import TimelineStorage
from .connection import get_feeds_collection


class MongoTimelineStorage(TimelineStorage):
    """
    Returns the serialized/dictified storage elements, not the actual Activity objects.
    Meant to be able to deal with Activities that aren't just Notifications.
    """
    def add_to_timeline(self, activity):
        raise NotImplementedError()

    def get_timeline(self, count=10, include_seen=False, level=None, verb=None, reverse=False):
        """
        :param count: int > 0
        :param include_seen: boolean
        :param level: Level or None
        :param verb: Verb or None
        """
        # TODO: input validation
        coll = get_feeds_collection()
        query = {
            "users": {"$all": [self.user_id]}
        }
        if not include_seen:
            query['unseen'] = [self.user_id]
        if level is not None:
            query['level'] = level.id
        if verb is not None:
            query['verb'] = verb.id
        order = pymongo.DESCENDING
        if reverse:
            order = pymongo.ASCENDING
        timeline = coll.find(query).sort("created", order)
        serial_notes = [note for note in timeline]
        return serial_notes

    def remove_from_timeline(self, activity_ids):
        raise NotImplementedError()

    def get_single_activity_from_timeline(self, note_id):
        coll = get_feeds_collection()
        query = {
            "id": note_id,
            "users": {"$all": [self.user_id]}
        }
        note_serial = coll.find_one(query)
        return note_serial
