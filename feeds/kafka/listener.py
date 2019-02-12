"""
Main controller class for the "app" that listens to Kafka.
In __init__, this sets up the environment and build the KafkaConsumer.
Activating it with start_listening() will run an endless loop that will
listen for notifications coming in from Kafka, and push them into
the Mongo feeds db by the same mechanism as the main server.
"""

from feeds.config import get_kafka_config
from .consumer import KafkaNotificationConsumer
import time


class KafkaListener(object):
    def __init__(self):
        kafka_cfg = get_kafka_config()
        self.consumer = KafkaNotificationConsumer(kafka_cfg.kafka_host,
                                                  kafka_cfg.kafka_topics,
                                                  kafka_cfg.kafka_group_id)

    def start_listening(self):
        while True:
            self.consumer.poll()
            time.sleep(1)
