import pytest
from feeds.kafka.listener import KafkaListener


def test_kafka_listener(kafka):
    listener = KafkaListener()
    assert listener.consumer is not None
