import pytest
from feeds.feeds.notification.notification_feed import NotificationFeed
from feeds.activity.notification import Notification

USER = "test_user"
USER_TYPE = "user"

def test_get_notifications(mongo_notes):
    """
    Imported the dataset. The main user is test_user, so get their feed in various ways.
    """
    feed = NotificationFeed(USER, USER_TYPE)
    # as NOT user_view, should be a list of Notification objects
    notes = feed.get_notifications()
    assert "feed" in notes and len(notes["feed"]) == 7
    assert "unseen" in notes and notes["unseen"] == 7
    for n in notes["feed"]:
        assert isinstance(n, Notification)

def test_get_notifications_fail(mongo_notes):
    feed = NotificationFeed(USER, USER_TYPE)
    with pytest.raises(ValueError) as e:
        feed.get_notifications(count=0)
    assert "Count must be an integer > 0" == str(e.value)

def test_update_timeline(mongo_notes):
    feed = NotificationFeed(USER, USER_TYPE)
    assert feed.timeline is None
    feed._update_timeline()
    assert feed.timeline is not None
    assert isinstance(feed.timeline, list)
    assert len(feed.timeline) == 7
    for n in feed.timeline:
        assert isinstance(n, dict)
