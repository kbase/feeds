from .base import FanoutModule
from feeds.config import get_config


class KBaseFanout(FanoutModule):
    def get_target_users(self):
        return [get_config().global_feed]
