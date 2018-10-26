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
    'db-engine=redis',
    'db-host=foo',
    'db-port=5',
    'auth-url=baz',
    'global-feed=global',
    'admins=admin1,admin2,admin3',
    'lifespan=30'
]

@pytest.fixture(scope="function")
def dummy_auth_token():
    backup_token = os.environ.get('AUTH_TOKEN')
    os.environ['AUTH_TOKEN'] = FAKE_AUTH_TOKEN
    yield
    del os.environ['AUTH_TOKEN']
    if backup_token is not None:
        os.environ['AUTH_TOKEN'] = backup_token

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

    feeds_config_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    cfg = config.FeedsConfig()
    assert cfg.auth_url == 'baz'
    assert cfg.db_host == 'foo'
    assert cfg.db_port == 5
    del os.environ['FEEDS_CONFIG']

    kb_dep_config = os.environ.get('KB_DEPLOYMENT_CONFIG')
    os.environ['KB_DEPLOYMENT_CONFIG'] = cfg_path
    cfg = config.FeedsConfig()
    assert cfg.auth_url == 'baz'
    assert cfg.db_host == 'foo'
    assert cfg.db_port == 5
    del os.environ['KB_DEPLOYMENT_CONFIG']
    if kb_dep_config is not None:
        os.environ['KB_DEPLOYMENT_CONFIG'] = path_backup

    if feeds_config_backup is not None:
        os.environ['FEEDS_CONFIG'] = feeds_config_backup


def test_config_from_env_errors(dummy_config, dummy_auth_token):
    cfg_lines = [
        '[not-feeds]',
        'db-host=foo'
    ]

    cfg_path = dummy_config(cfg_lines)
    path_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Error parsing config file: section feeds not found!" in str(e.value)
    del os.environ['FEEDS_CONFIG']
    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup

def test_config_from_env_no_auth():
    backup_token = os.environ.get('AUTH_TOKEN')
    if 'AUTH_TOKEN' in os.environ:
        del os.environ['AUTH_TOKEN']
    with pytest.raises(RuntimeError) as e:
        config.FeedsConfig()
    assert "The AUTH_TOKEN environment variable must be set!" in str(e.value)
    if backup_token is not None:
        os.environ['AUTH_TOKEN'] = backup_token

def test_get_config(dummy_config, dummy_auth_token):
    cfg_path = dummy_config(GOOD_CONFIG)

    path_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    config.__config = None

    cfg = config.get_config()
    assert cfg.db_host == 'foo'
    assert cfg.db_port == 5
    assert cfg.auth_url == 'baz'
    assert cfg.auth_token == FAKE_AUTH_TOKEN
    del os.environ['FEEDS_CONFIG']
    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup
    config.__config = None