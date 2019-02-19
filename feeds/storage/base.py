from feeds.entity.entity import Entity


class BaseStorage(object):
    def __init__(self):
        pass

    def serialize(self):
        raise NotImplementedError()

    def deserialize(self):
        raise NotImplementedError()


class ActivityStorage(BaseStorage):
    def __init__(self):
        pass

    def add_to_storage(self, activities):
        raise NotImplementedError()

    def get_from_storage(self, activity_ids):
        raise NotImplementedError()

    def remove_from_storage(self, activity_ids):
        raise NotImplementedError()


class TimelineStorage(BaseStorage):
    def __init__(self, user_id, user_type):
        assert user_id
        assert user_type
        self.user_id = user_id
        self.user_type = user_type  # should align with entity types
        self.user = Entity(user_id, user_type)

    def add_to_timeline(self, activity):
        raise NotImplementedError()

    def get_timeline(self, count=10):
        raise NotImplementedError()

    def remove_from_timeline(self, activity_ids):
        raise NotImplementedError()
