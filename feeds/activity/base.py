from abc import abstractmethod


class BaseActivity(object):
    """
    Common parent class for Activity and Notification.
    Activity will be done later. But a Notification is an Activity.
    """
    @abstractmethod
    def to_dict(self):
        pass
