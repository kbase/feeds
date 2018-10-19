USER_FEED_KEY = "feed:user:{}"

def get_user_key(user):
    return USER_FEED_KEY.format(user)

def get_note_id(note):
    return "{}-{}".format(note.source, note.id)