class BaseFeed(object):
    """
    A feed should keep track of a user's activities. It should know how to add to them, fetch them,
    and store them. It does NOT know how to fan those out to other feeds. It's just a really
    fancy, database-powered list of Activities.
    """