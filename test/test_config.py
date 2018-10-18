import pytest
from feeds import config
from feeds.exceptions import ConfigError
from unittest import mock
from pathlib import Path
import os

# TODO - more error checking

FAKE_AUTH_TOKEN = "I'm an auth token!"

def write_test_cfg(path, cfg_lines):
    if os.path.exists(path):
        raise ValueError("Not gonna overwrite some existing file with this test stuff!")
    with open(path, "w") as f:
        f.write("\n".join(cfg_lines))

def test_config_from_env_ok():
    cfg_lines = [
        '[feeds]',
        'redis-host=foo',
        'redis-port=bar',
        'auth-url=baz'
    ]
    cfg_path = "fake_test_config_delete_me.cfg"
    write_test_cfg(cfg_path, cfg_lines)

    os.environ['AUTH_TOKEN'] = FAKE_AUTH_TOKEN

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
    del os.environ['AUTH_TOKEN']
    os.remove(cfg_path)

def test_config_from_env_errors():
    os.environ['AUTH_TOKEN'] = FAKE_AUTH_TOKEN
    cfg_lines = [
        '[not-feeds]',
        'redis-host=foo'
    ]
    cfg_path = "fake_test_config_delete_me.cfg"
    write_test_cfg(cfg_path, cfg_lines)
    os.environ['FEEDS_CONFIG'] = cfg_path
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Error parsing config file: section feeds not found!" in str(e.value)

    del os.environ['AUTH_TOKEN']
    del os.environ['FEEDS_CONFIG']
    os.remove(cfg_path)

def test_config_from_env_no_auth():
    with pytest.raises(RuntimeError) as e:
        config.FeedsConfig()
    assert "The AUTH_TOKEN environment variable must be set!" in str(e.value)

def test_get_config():
    cfg_lines = [
        '[feeds]',
        'redis-host=foo',
        'redis-port=bar',
        'auth-url=baz'
    ]
    cfg_path = "fake_test_config_delete_me.cfg"
    write_test_cfg(cfg_path, cfg_lines)
    os.environ['FEEDS_CONFIG'] = cfg_path
    os.environ['AUTH_TOKEN'] = FAKE_AUTH_TOKEN

    cfg = config.get_config()
    assert cfg.redis_host == 'foo'
    assert cfg.redis_port == 'bar'
    assert cfg.auth_url == 'baz'
    assert cfg.auth_token == FAKE_AUTH_TOKEN
    os.remove("fake_test_config_delete_me.cfg")
    del os.environ['FEEDS_CONFIG']
    del os.environ['AUTH_TOKEN']