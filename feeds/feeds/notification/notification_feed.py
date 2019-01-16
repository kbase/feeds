from ..base import BaseFeed
from feeds.activity.notification import Notification
from feeds.storage.mongodb.activity_storage import MongoActivityStorage
from feeds.storage.mongodb.timeline_storage import MongoTimelineStorage
from cachetools import TTLCache
import logging
from feeds.exceptions import NotificationNotFoundError
from feeds.entity.entity import Entity
from typing import (
    List,
    Dict
)


class NotificationFeed(BaseFeed):
    def __init__(self, user_id: str, user_type: str, token: str=None):
        self.user = Entity(user_id, user_type, token=token)
        self.token = token
        self.timeline_storage = MongoTimelineStorage(user_id, user_type)
        self.activity_storage = MongoActivityStorage()
        self.timeline = None
        self.cache = TTLCache(1000, 600)

    def _update_timeline(self) -> None:
        """
        Updates a local user timeline cache. This is a list of activity ids
        that are used for fetching from activity storage (for now). Sorted
        by newest first.

        TODO: add metadata to timeline storage - type and verb, first.
        """
        logging.getLogger(__name__).info(
            'Fetching timeline for '.format(self.user)
        )
        self.timeline = self.timeline_storage.get_timeline()

    def get_group_notifications(self, group: Dict[str, str], count: int=10,
                                include_seen: bool=False, level=None,
                                verb=None, reverse: bool=False) -> dict:
        """
        Returns all notifications (using the get_notifications fn.) for a user, filtered down to
        those that reference an Entity of type group with the given id.
        """
        notes = self.get_notifications(count=count, include_seen=include_seen, level=level,
                                       verb=verb, reverse=reverse)
        # group has id and name keys
        group_notes = {
            "unseen": 0,
            "name": group.get("name"),
            "feed": list()
        }
        gid = group["id"]

        def is_group(e: Entity) -> bool:
            return e.id == gid and e.type == "group"

        notes_list = list()
        for n in notes["feed"]:
            if is_group(n.actor) or is_group(n.object) or any([is_group(t) for t in n.target]):
                notes_list.append(n)
                if not n.seen:
                    group_notes["unseen"] += 1
        Notification.update_entity_names(notes_list, token=self.token)
        for n in notes_list:
            group_notes["feed"].append(n.user_view())
        return group_notes

    def get_notifications(self, count: int=10, include_seen: bool=False, level=None, verb=None,
                          reverse: bool=False, user_view: bool=False) -> dict:
        """
        Fetches all activities matching the requested inputs.
        :param count: max number of most recent notifications to return. default=10
        :param include_seen: include notifications that have been seen in the response.
            default = False
        :param level: if not None, will only return notifications of the given level.
            default = None
        :param verb: if not None, will only return notifications made with the given verb.
            default = None
        :param reverse: if True, will reverse the order of the result (default False)
        :param user_view: if True, will return the user_view dict version of each Notification
            object. If False, will return a list of Notification objects instead. default False
        :return: a dict with the requested notifications, and a key with the total number in the
            feed that are marked unseen
        :rtype: dict
        :raises ValueError: if count <= 0
        """
        activities = self.get_activities(
            count=count, include_seen=include_seen, verb=verb,
            level=level, reverse=reverse, user_view=user_view
        )
        ret_struct = {
            "unseen": self.get_unseen_count(),
            "name": self.user.name
        }
        if user_view:
            ret_struct["feed"] = list()
            Notification.update_entity_names(activities, token=self.token)
            for act in activities:
                ret_struct["feed"].append(act.user_view())
        else:
            ret_struct["feed"] = activities
        return ret_struct

    def get_notification(self, note_id):
        """
        Returns a single notification.
        If it doesn't exist (either the user can't see it, or it's really not there), raises
        a NotificationNotFoundError.
        """
        note = self.timeline_storage.get_single_activity_from_timeline(note_id)
        if note is None:
            raise NotificationNotFoundError("Cannot find notification with id {}.".format(note_id))
        else:
            return Notification.from_dict(note, self.token)

    def get_activities(self, count=10, include_seen=False, level=None, verb=None,
                       reverse=False, user_view=False) -> List[Notification]:
        """
        Returns a selection of activities.
        :param count: Maximum number of Notifications to return (default 10)
        """
        # steps.
        # 0. If in cache, return them.  <-- later
        # 1. Get storage adapter.
        # 2. Query it for recent activities from this user.
        # 3. Cache them here.
        # 4. Return them.
        if count < 1 or not isinstance(count, int):
            raise ValueError("Count must be an integer > 0")
        serial_notes = self.timeline_storage.get_timeline(
            count=count, include_seen=include_seen,
            level=level, verb=verb, reverse=reverse
        )
        note_list = list()
        user_dict = self.user.to_dict()
        for note in serial_notes:
            if user_dict in note["unseen"]:
                note["seen"] = False
            else:
                note["seen"] = True
            note_list.append(Notification.from_dict(note, self.token))
        return note_list

    def mark_activities(self, activity_ids, seen=False):
        """
        Marks the given list of activities as either seen (True) or unseen (False).
        If the owner of this feed is not on the users list for an activity, nothing is
        changed for that activity.
        """
        if seen:
            self.activity_storage.set_seen(activity_ids, self.user)
        else:
            self.activity_storage.set_unseen(activity_ids, self.user)

    def add_notification(self, note):
        return self.add_activity(note)

    def add_activity(self, note):
        """
        Adds an activity to this user's feed
        """
        self.activity_storage.add_to_storage(note, [self.user])

    def get_unseen_count(self):
        """
        Returns the number of unread / unexpired notifications in this feed.
        """
        return self.timeline_storage.get_unseen_count()
