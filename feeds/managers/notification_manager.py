"""
A NotificationManager manages adding new notifications.
This is separate from a feed - notifications get added by the KBase system to
user feeds, based on the content and context of the Notification.

See also the docs in NotificationFeed.
"""

from typing import List
from .base import BaseManager
from ..activity.notification import Notification
from ..storage.mongodb.activity_storage import MongoActivityStorage
from feeds.config import get_config
from .fanout_modules.groups import GroupsFanout
from .fanout_modules.workspace import WorkspaceFanout
from .fanout_modules.jobs import JobsFanout
from .fanout_modules.kbase import KBaseFanout


class NotificationManager(BaseManager):
    def __init__(self):
        # init storage
        pass

    def add_notification(self, note: Notification):
        """
        Adds a new notification.
        Triggers validation first.
        """
        note.validate()  # any errors get raised to be caught by the server.
        target_users = self.get_target_users(note)
        # add the notification to the database.
        activity_storage = MongoActivityStorage()
        activity_storage.add_to_storage(note, target_users)

    def get_target_users(self, note: Notification) -> List[str]:
        """
        This is gonna get complex.
        The target users are a combination of:
        - the list in note.target
        - workspace admins (if it comes from a workspace)
        - everyone, if it's global - mark as _global_ feed.
        TODO: add adapters, maybe subclass notifications to handle each source?
        """
        fanout = None
        if note.source == 'ws' or note.source == 'workspace':
            fanout = WorkspaceFanout(note)
        elif note.source == 'groups':
            fanout = GroupsFanout(note)
        elif note.source == 'jobs':
            fanout = JobsFanout(note)
        elif note.source == 'kbase':
            fanout = KBaseFanout(note)

        if fanout is not None:
            user_list = fanout.get_target_users()
        else:
            user_list = list(set(note.users + note.target))

        return user_list

    def expire_notifications(self, note_ids: list, external_keys: list, source: str=None, is_admin: bool=False):
        """
        Expires notifications.
        All notifications identified by either their id, or external key, must come from the same
        source as in the source parameter (i.e. the 'source' key in the database must == the source).
        Or, an admin can expire any notification.
        """
        # Get the notifications from the note_ids and external_keys.
        # -- mark as unauthorized the ones that don't exist.
        # If is_admin, cool, expire them all.
        # If source is not None and not is_admin, make a list of the ones that can be expired (from that source)
        # expire the ones that we should.
        # return the results.

        storage = MongoActivityStorage()

        notes_from_id = storage.get_by_id(note_ids, source=source)
        notes_from_ext_key = {}
        if source is not None and len(external_keys):
            notes_from_ext_key = storage.get_by_external_key(external_keys, source)
        unauthorized = {
            "note_ids": [k for k in notes_from_id if notes_from_id[k] is None],
            "external_keys": [k for k in notes_from_ext_key if notes_from_ext_key[k] is None]
        }
        ids_to_expire = list()
        expired = {"note_ids": [], "external_keys": []}
        for k,v in notes_from_id.items():
            if v is not None:
                ids_to_expire.append(k)
                expired["note_ids"].append(k)
        for k,v in notes_from_ext_key.items():
            if v is not None:
                ids_to_expire.append(v['id'])
                expired["external_keys"].append(v['external_key'])
        storage.expire_notifications(ids_to_expire)
        return {
            "unauthorized": unauthorized,
            "expired": expired
        }