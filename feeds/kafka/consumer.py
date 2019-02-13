from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from typing import List
import json
from feeds.api.util import parse_notification_params
from feeds.logger import (
    log,
    log_error
)
from feeds.activity.notification import Notification
from feeds.managers.notification_manager import NotificationManager


class KafkaNotificationConsumer(object):
    def __init__(self, server: str, topics: List[str], group_id: str) -> None:
        self.server = server
        self.topics = topics
        self.group_id = group_id
        self.consumer = KafkaConsumer(topics[0],
                                      client_id="feeds-kakfa-consumer",
                                      bootstrap_servers=[server],
                                      consumer_timeout_ms=1000,
                                      group_id=group_id,
                                      enable_auto_commit=True,
                                      auto_commit_interval_ms=1000,
                                      auto_offset_reset="earliest")

    def poll(self) -> None:
        for msg in self.consumer:
            print(msg)
            self._process_message(msg)

    def _process_message(self, message: ConsumerRecord) -> None:
        try:
            note_params = parse_notification_params(json.loads(message.value))
            # create a Notification from params.
            new_note = Notification(
                note_params.get('actor'),
                note_params.get('verb'),
                note_params.get('object'),
                note_params.get('source'),
                level=note_params.get('level'),
                target=note_params.get('target', []),
                context=note_params.get('context'),
                expires=note_params.get('expires'),
                external_key=note_params.get('external_key'),
                users=note_params.get('users', [])
            )
            # pass it to the NotificationManager to dole out to its audience feeds.
            manager = NotificationManager()
            manager.add_notification(new_note)
            log(__name__, "Created notification from Kafka with id {}".format(new_note.id))
        except Exception as e:
            log_error(__name__, e)

    def __str__(self):
        return ("KafkaNotificationConsumer: host:{},group_id:{},"
                "topics:{}".format(self.server, self.group_id, self.topics))
