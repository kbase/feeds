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
        self.consumer = KafkaConsumer(bootstrap_servers=server,
                                      auto_offset_reset='latest',
                                      group_id=group_id,
                                      enable_auto_commit=True)
        self.consumer.subscribe(topics)

    def poll(self) -> None:
        for msg in self.consumer:
            self._process_message(msg)
        self.consumer.commit()

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
