import pytest
import json
from kafka import (KafkaProducer, TopicPartition)
from feeds.kafka.consumer import KafkaNotificationConsumer
import test.util as test_util
from feeds.config import get_kafka_config
import time
from uuid import uuid4


def test_kafka_consumer(client, kafka, mongo, mock_valid_users, mock_valid_user_token):
    user = "test_consumer"
    cfg = get_kafka_config()
    # set up consumer
    consumer = KafkaNotificationConsumer(cfg.kafka_host, cfg.kafka_topics, cfg.kafka_group_id)
    # set up producer
    producer = KafkaProducer(bootstrap_servers=cfg.kafka_host)
    topic = cfg.kafka_topics[0]
    # make a notification post
    mock_valid_users({"kafkatest": "KBase Test", user: "Test Consumer"})
    mock_valid_user_token(user, "Test Consumer")

    note = {
        "actor": { "type": "user", "id": "kafkatest" },
        "verb": "invite",
        "object": { "type": "user", "id": user },
        "target": [{ "type": "user", "id": user }],
        "users": [{ "type": "user", "id": user }],
        "level": "alert",
        "source": "a_service",
        "context": {
            "foo": "bar"
        }
    }
    producer.send(topic, bytes(json.dumps(note), "utf-8"))
    producer.flush()
    time.sleep(3)
    consumer.poll()

    # fetch notifications and expect that our new one is in there
    response = client.get("/api/V1/notifications", headers={"Authorization": "token-"+str(uuid4())})
    data = json.loads(response.data)
    assert len(data["user"]["feed"]) == 1
    note = data["user"]["feed"][0]
    assert note['actor'] == {"type": "user", "id": "kafkatest", "name": "KBase Test"}
    assert note['context'] == {"foo": "bar"}
    # consumer.consumer.close()


def test_bad_input(kafka):
    """
    Expect to log and continue.
    """
    user = "test_consumer"
    cfg = get_kafka_config()
    # set up consumer
    consumer = KafkaNotificationConsumer(cfg.kafka_host, cfg.kafka_topics, cfg.kafka_group_id)
    # set up producer
    producer = KafkaProducer(bootstrap_servers=cfg.kafka_host)
    topic = cfg.kafka_topics[0]
    # no object or actor!
    note = {
        "verb": "invite",
        "target": [{ "type": "user", "id": user }],
        "users": [{ "type": "user", "id": user }],
        "level": "alert",
        "source": "a_service",
        "context": {
            "foo": "bar"
        }
    }
    producer.send(topic, bytes(json.dumps(note), "utf-8"))
    producer.flush()
    print("COMMITTED: {}".format(consumer.consumer.committed(TopicPartition("feeds", 0))))
    time.sleep(3)
    consumer.poll()
    # consumer.consumer.close()
