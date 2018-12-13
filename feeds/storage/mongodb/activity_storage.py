from typing import List
from ..base import ActivityStorage
from .connection import get_feeds_collection
from feeds.exceptions import (
    ActivityStorageError
)
from pymongo.errors import PyMongoError
from feeds.util import epoch_ms


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

    def get_by_id(self, act_ids: List[str], source: str=None):
        """
        If source is not None, return only those that match the source.
        Returns a dict mapping from note id to note
        """
        if len(act_ids) == 0:
            return {}
        coll = get_feeds_collection()
        query = {
            'id': {'$in': act_ids}
        }
        if source is not None:
            query['source'] = source
        notes = {k: None for k in act_ids}
        curs = coll.find(query)
        for d in curs:
            notes[d["id"]] = d
        return notes

    def get_by_external_key(self, external_keys: List[str], source):
        """
        Source HAS to exist here, it's part of the index.
        Returns a dict mapping from external_key to note
        """
        assert source is not None
        if len(external_keys) == 0:
            return {}
        coll = get_feeds_collection()
        query = {
            'external_key': {'$in': external_keys},
            'source': source
        }
        notes = {k: None for k in external_keys}
        curs = coll.find(query)
        for d in curs:
            notes[d["external_key"]] = d
        return notes

    def expire_notifications(self, act_ids: List[str]):
        """
        Expires notifications by changing their expiration time to now.
        """
        now = epoch_ms()
        coll = get_feeds_collection()
        coll.update_many({
            'id': {'$in': act_ids}
        }, {
            '$set': {'expires': now}
        })
