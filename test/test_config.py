import pytest
from feeds import config
from feeds.exceptions import ConfigError
from unittest import mock
from pathlib import Path
import os
from tempfile import mkstemp

# TODO - more error checking

FAKE_AUTH_TOKEN = "I'm an auth token!"

GOOD_CONFIG = [
    '[feeds]',
    'redis-host=foo',
    'redis-port=bar',
    'auth-url=baz',
    'global-feed=global',
    'admins=admin1,admin2,admin3'
]

@pytest.fixture(scope="function")
def dummy_auth_token():
    os.environ['AUTH_TOKEN'] = FAKE_AUTH_TOKEN
    yield
    del os.environ['AUTH_TOKEN']

@pytest.fixture(scope="function")
def dummy_config():
    (f, fname) = mkstemp(text=True)

    def _write_test_cfg(cfg_lines):
        with open(fname, 'w') as cfg:
            cfg.write("\n".join(cfg_lines))
        return fname

    yield _write_test_cfg
    os.remove(fname)


def test_config_from_env_ok(dummy_config, dummy_auth_token):
    cfg_path = dummy_config(GOOD_CONFIG)

    os.environ['FEEDS_CONFIG'] = cfg_path
    cfg = config.FeedsConfig()
    assert cfg.auth_url == 'baz'
    assert cfg.redis_host == 'foo'
    assert cfg.redis_port == 'bar'
    del os.environ['FEEDS_CONFIG']

    os.environ['KB_DEPLOYMENT_CONFIG'] = cfg_path
    cfg = config.FeedsConfig()
    assert cfg.auth_url == 'baz'
    assert cfg.redis_host == 'foo'
    assert cfg.redis_port == 'bar'

    del os.environ['KB_DEPLOYMENT_CONFIG']


def test_config_from_env_errors(dummy_config, dummy_auth_token):
    cfg_lines = [
        '[not-feeds]',
        'redis-host=foo'
    ]

    cfg_path = dummy_config(cfg_lines)
    os.environ['FEEDS_CONFIG'] = cfg_path
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Error parsing config file: section feeds not found!" in str(e.value)
    del os.environ['FEEDS_CONFIG']


def test_config_from_env_no_auth():
    with pytest.raises(RuntimeError) as e:
        config.FeedsConfig()
    assert "The AUTH_TOKEN environment variable must be set!" in str(e.value)

def test_get_config(dummy_config, dummy_auth_token):
    cfg_path = dummy_config(GOOD_CONFIG)
    os.environ['FEEDS_CONFIG'] = cfg_path

    cfg = config.get_config()
    assert cfg.redis_host == 'foo'
    assert cfg.redis_port == 'bar'
    assert cfg.auth_url == 'baz'
    assert cfg.auth_token == FAKE_AUTH_TOKEN
    os.remove("fake_test_config_delete_me.cfg")
    del os.environ['FEEDS_CONFIG']