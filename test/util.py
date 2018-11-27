import uuid
import socket
from contextlib import closing
from pathlib import Path
import os
import tempfile
import configparser

MONGO_EXE = "mongo-exe"
TEMP_DIR = "test-temp-dir"
DELETE_TEMP_FILES = "delete-temp-files"


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

def get_temp_dir() -> Path:
    cfg = test_config()
    return Path(os.path.abspath(cfg.get('test', TEMP_DIR)))

def get_delete_temp_files() -> bool:
    cfg = test_config()
    return cfg.get('test', DELETE_TEMP_FILES).lower() == "true"

def test_config():
    """
    Returns a ConfigParser.
    Because I'm lazy.
    """
    cfg = configparser.ConfigParser()
    with open(os.environ['FEEDS_CONFIG'], 'r') as f:
        cfg.read_file(f)
    return cfg
