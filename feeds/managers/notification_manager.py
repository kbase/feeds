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
            user_list = list()
            if note.target:
                user_list = user_list + note.target
            elif note.source == 'kbase':
                user_list.append(get_config().global_feed)
        return user_list
