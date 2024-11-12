import pymongo
from ..base import TimelineStorage
from .connection import get_feeds_collection
from feeds.util import epoch_ms
from feeds.activity.base import BaseActivity
from feeds.notification_level import Level
from feeds.verbs import Verb
from typing import (
    List,
    Dict
)


class MongoTimelineStorage(TimelineStorage):
    """
    Returns the serialized/dictified storage elements, not the actual Activity objects.
    Meant to be able to deal with Activities that aren't just Notifications.
    """
    def add_to_timeline(self, activity: BaseActivity) -> None:
        raise NotImplementedError()

    def get_timeline(self, count: int=10, include_seen: int=False, level: Level=None,
                     verb: Verb=None, reverse: bool=False) -> List[dict]:
        """
        :param count: int > 0
        :param include_seen: boolean
        :param level: Level or None
        :param verb: Verb or None
        """
        coll = get_feeds_collection()
        now = epoch_ms()
        query = {
            "users": self._user_doc(),
            "expires": {"$gt": now}
        }
        if not include_seen:
            query['unseen'] = self._user_doc()
        if level is not None:
            query['level'] = level.id
        if verb is not None:
            query['verb'] = verb.id
        order = pymongo.DESCENDING
        if reverse:
            order = pymongo.ASCENDING
        timeline = coll.find(query).sort("created", order).limit(count)
        serial_notes = [note for note in timeline]
        return serial_notes

    def get_single_activity_from_timeline(self, note_id: str) -> dict:
        coll = get_feeds_collection()
        query = {
            "id": note_id,
            "users": self._user_doc()
        }
        note_serial = coll.find_one(query)
        if note_serial is None:
            return None
        if self.user.to_dict() in note_serial['unseen']:
            note_serial['seen'] = False
        else:
            note_serial['seen'] = True
        return note_serial

    def get_unseen_count(self) -> int:
        coll = get_feeds_collection()
        now = epoch_ms()
        query = {
            "users": self._user_doc(),
            "unseen": self._user_doc(),
            "expires": {"$gt": now}
        }
        return coll.count_documents(query)

    def _user_doc(self) -> Dict[str, str]:
        return {
            "id": self.user_id,
            "type": self.user_type
        }
