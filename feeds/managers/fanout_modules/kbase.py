from .base import FanoutModule
from feeds.config import get_config
from feeds.entity import Entity


class KBaseFanout(FanoutModule):
    def get_target_users(self):
        cfg = get_config()
        return [Entity(cfg.global_feed, cfg.global_feed_type)]
