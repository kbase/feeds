from typing import List
from ..base import ActivityStorage
from .connection import get_feeds_collection
from feeds.exceptions import (
    ActivityStorageError,
    ActivityRetrievalError
)

class MongoActivityStorage(ActivityStorage):
    def add_to_storage(self, activity, target_users: List[str]):
        """
        Adds a single activity to the MongoDB.
        Returns None if successful.
        Raises an ActivityStorageError if it fails.
        """
        coll = get_feeds_collection()
        act_doc = {
            "act_id": activity.id,
            "actor": activity.actor,
            "verb": activity.verb.id,
            "object": activity.object,
            "target": activity.target,
            "source": activity.source,
            "level": activity.level.id,
            "users": target_users,
            "unseen": target_users,
            "created": activity.time,
            "context": activity.context
        }
        try:
            coll.insert_one(act_doc)
        except e:
            raise ActivityStorageError("Failed to store activity: " + str(e))

    def get_from_storage(self, activity_ids):
        pass

    def remove_from_storage(self, activity_ids):
        raise NotImplementedError()

    def change_seen_mark(self, act_id: str, user: str, seen: bool):
        """
        :param act_id: activity id
        :user: user id
        :seen: whether or not it's been seen. Boolean.
        """
        raise NotImplementedError()