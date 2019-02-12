import uuid
import socket
from contextlib import closing
from pathlib import Path
import os
import tempfile
import configparser

MONGO_EXE = "mongo-exe"
MONGO_TEMP_DIR = "mongo-temp-dir"
DELETE_MONGO_FILES = "delete-mongo-files"
KAFKA_PATH = "kafka-path"
KAFKA_CONFIG = "kafka-config"
ZOOKEEPER_CONFIG = "zookeeper-config"
KAFKA_TEMP_DIR = "kafka-temp-dir"
DELETE_KAFKA_FILES = "delete-kafka-files"


def assert_is_uuid(s):
    # raises a ValueError if not. Good enough for testing.
    uuid.UUID(s)


class TestException(Exception):
    pass


def get_mongo_exe() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', MONGO_EXE)))


def find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def get_mongo_temp_dir() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', MONGO_TEMP_DIR)))


def get_kafka_temp_dir() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', KAFKA_TEMP_DIR)))


def get_delete_mongo_files() -> bool:
    cfg = test_config()
    return cfg.get('test', DELETE_MONGO_FILES).lower() == "true"


def get_delete_kafka_files() -> bool:
    cfg = test_config()
    return cfg.get('test', DELETE_KAFKA_FILES)

def test_config():
    """
    Returns a ConfigParser.
    Because I'm lazy.
    """
    cfg = configparser.ConfigParser()
    with open(os.environ['FEEDS_CONFIG'], 'r') as f:
        cfg.read_file(f)
    return cfg


def get_kafka_root() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', KAFKA_PATH)))


def get_kafka_config() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', KAFKA_CONFIG)))


def get_zookeeper_config() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', ZOOKEEPER_CONFIG)))
