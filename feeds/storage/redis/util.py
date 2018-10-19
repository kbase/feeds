from feeds.activity.base import BaseActivity

USER_FEED_KEY = "feed:user:{}"
ACTIVITY_STORAGE_KEY = "notes:{}"

def get_user_key(user):
    return USER_FEED_KEY.format(user)

def get_note_id(note):
    return "{}-{}".format(note.source, note.id)

def get_activity_key(activity):
    if isinstance(activity, bytes):
        return ACTIVITY_STORAGE_KEY.format(activity.decode('utf-8')[0])
    elif hasattr(activity, "id"):
        return ACTIVITY_STORAGE_KEY.format(activity.id[0])
    else:
        return ACTIVITY_STORAGE_KEY.format(activity[0])