from kafka import (
    KafkaConsumer
)
from kafka.consumer.fetcher import ConsumerRecord
from typing import List


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
        print(message)


