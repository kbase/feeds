from typing import List
from ..base import ActivityStorage
from .connection import get_feeds_collection
from feeds.exceptions import (
    ActivityStorageError
)
from pymongo.errors import PyMongoError


class MongoActivityStorage(ActivityStorage):
    def add_to_storage(self, activity, target_users: List[str]):
        """
        Adds a single activity to the MongoDB.
        Returns None if successful.
        Raises an ActivityStorageError if it fails.
        """
        coll = get_feeds_collection()
        act_doc = activity.to_dict()
        act_doc["users"] = target_users
        act_doc["unseen"] = target_users
        try:
            coll.insert_one(act_doc)
        except PyMongoError as e:
            raise ActivityStorageError("Failed to store activity: " + str(e))

    def get_from_storage(self, activity_ids):
        pass

    def remove_from_storage(self, activity_ids):
        raise NotImplementedError()

    def set_unseen(self, act_ids: List[str], user: str):
        """
        Setting unseen means adding the user to the list of unseens. But we should only do that for
        docs that the user can't see anyway, so put that in the query.
        """
        coll = get_feeds_collection()
        coll.update_many({
            'id': {'$in': act_ids},
            'users': {'$all': [user]},
            'unseen': {'$nin': [user]}
        }, {
            '$addToSet': {'unseen': user}
        })

    def set_seen(self, act_ids: List[str], user: str):
        """
        Setting seen just means removing the user from the list of unseens.
        The query should find all docs in the list of act_ids, where the user
        is in the list of users, AND the list of unseens.
        The update should remove the user from the list of unseens.
        """
        coll = get_feeds_collection()
        coll.update_many({
            'id': {'$in': act_ids},
            'users': {'$all': [user]},
            'unseen': {'$all': [user]}
        }, {
            '$pull': {'unseen': user}
        })