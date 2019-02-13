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
    'njs-url=njs',
    'workspace-url=ws',
    'groups-url=groups',
    'nms-url=nms',
    'global-feed=global',
    'lifespan=30',
    'default-note-count=100',
    '[kafka]',
    'host=localhost:9092',
    'topics=foo,bar',
    'group-id=feeds_group'
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

@pytest.mark.parametrize("bad_val", [("foo"), (-100), (0), (0.5)])
def test_config_bad_port(dummy_config, dummy_auth_token, bad_val):
    cfg_text = GOOD_CONFIG.copy()
    cfg_text[3] = "db-port=wrong"
    cfg_path = dummy_config(cfg_text)
    feeds_config_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "db-port must be an int > 0! Got wrong" == str(e.value)
    del os.environ['FEEDS_CONFIG']
    if feeds_config_backup is not None:
        os.environ['FEEDS_CONFIG'] = feeds_config_backup


@pytest.mark.parametrize("bad_val", [("foo"), (-100), (0), (0.5)])
def test_config_bad_lifespan(dummy_config, dummy_auth_token, bad_val):
    cfg_text = GOOD_CONFIG.copy()
    cfg_text[10] = "lifespan=wrong"
    cfg_path = dummy_config(cfg_text)
    feeds_config_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "lifespan must be an int > 0! Got wrong" == str(e.value)
    del os.environ['FEEDS_CONFIG']
    if feeds_config_backup is not None:
        os.environ['FEEDS_CONFIG'] = feeds_config_backup


@pytest.mark.parametrize("bad_val", [("foo"), (-100), (0), (0.5)])
def test_config_bad_note_count(dummy_config, dummy_auth_token, bad_val):
    cfg_text = GOOD_CONFIG.copy()
    cfg_text[11] = "default-note-count={}".format(bad_val)
    cfg_path = dummy_config(cfg_text)
    feeds_config_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "default-note-count must be an int > 0! Got {}".format(bad_val) == str(e.value)
    del os.environ["FEEDS_CONFIG"]
    if feeds_config_backup is not None:
        os.environ['FEEDS_CONFIG'] = feeds_config_backup


def test_config_check_debug(dummy_config, dummy_auth_token):
    cfg_text = GOOD_CONFIG.copy()
    cfg_text.insert(1, "debug=true")
    cfg_path = dummy_config(cfg_text)
    feeds_config_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    assert config.FeedsConfig().debug == True
    del os.environ['FEEDS_CONFIG']
    if feeds_config_backup is not None:
        os.environ['FEEDS_CONFIG'] = feeds_config_backup


def test_config_from_env_ok(dummy_config, dummy_auth_token):
    cfg_path = dummy_config(GOOD_CONFIG)

    feeds_config_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    cfg = config.FeedsConfig()
    assert cfg.auth_url == 'baz'
    assert cfg.db_host == 'foo'
    assert cfg.db_port == 5
    assert cfg.debug == False
    del os.environ['FEEDS_CONFIG']

    kb_dep_config = os.environ.get('KB_DEPLOYMENT_CONFIG')
    os.environ['KB_DEPLOYMENT_CONFIG'] = cfg_path
    cfg = config.FeedsConfig()
    assert cfg.auth_url == 'baz'
    assert cfg.db_host == 'foo'
    assert cfg.db_port == 5
    assert cfg.debug == False
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


def test_config_not_found():
    feeds_cfg_key = 'FEEDS_CONFIG'
    depl_cfg_key = 'KB_DEPLOYMENT_CONFIG'
    feeds_config_bu = os.environ.get(feeds_cfg_key)
    deploy_config_bu = os.environ.get(depl_cfg_key)
    default_file = os.path.join(os.path.dirname(__file__), '..', 'deploy.cfg')
    renamed_file = os.path.join(os.path.dirname(__file__), '..', 'deploy-bak-temp-stuff.cfg')
    was_renamed = False

    if feeds_cfg_key in os.environ:
        del os.environ[feeds_cfg_key]
    if depl_cfg_key in os.environ:
        del os.environ[depl_cfg_key]
    if os.path.exists(default_file):
        os.rename(default_file, renamed_file)
        was_renamed = True

    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Unable to find config file" in str(e.value)

    if feeds_config_bu is not None:
        os.environ[feeds_cfg_key] = feeds_config_bu
    if deploy_config_bu is not None:
        os.environ[depl_cfg_key] = deploy_config_bu
    if was_renamed:
        os.rename(renamed_file, default_file)


def test_config_bad_path(dummy_auth_token):
    feeds_cfg_key = 'FEEDS_CONFIG'
    depl_cfg_key = 'KB_DEPLOYMENT_CONFIG'
    feeds_config_bu = os.environ.get(feeds_cfg_key)
    deploy_config_bu = os.environ.get(depl_cfg_key)

    if depl_cfg_key in os.environ:
        del os.environ[depl_cfg_key]
    os.environ[feeds_cfg_key] = "/not/a/real/path/fail"
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Environment variable FEEDS_CONFIG is set to" in str(e.value)
    if feeds_config_bu is not None:
        os.environ[feeds_cfg_key] = feeds_config_bu
    else:
        del os.environ[feeds_cfg_key]
    if deploy_config_bu is not None:
        os.environ[depl_cfg_key] = deploy_config_bu


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

    cfg = config.get_kafka_config()
    assert cfg.kafka_group_id == 'feeds_group'
    assert cfg.kafka_host == 'localhost:9092'
    assert cfg.kafka_topics == ['foo', 'bar']

    del os.environ['FEEDS_CONFIG']
    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup
    config.__config = None


def test_config_missing_section(dummy_config, dummy_auth_token):
    cfg_path = dummy_config(["[fleeble]"])
    path_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    config.__config = None
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Error parsing config file: section feeds not found" in str(e.value)
    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup


def test_config_missing_reqs(dummy_config, dummy_auth_token):
    path_backup = os.environ.get('FEEDS_CONFIG')
    bad_cfg_1 = [
        "[feeds]",
        "db-engine=mongodb"
    ]
    cfg_path = dummy_config(bad_cfg_1)
    os.environ['FEEDS_CONFIG'] = cfg_path
    config.__config = None
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "not found in config" in str(e.value)

    bad_cfg_2 = [
        "[feeds]",
        "db-engine="
    ]
    cfg_path2 = dummy_config(bad_cfg_2)
    os.environ['FEEDS_CONFIG'] = cfg_path2
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "has no value!" in str(e.value)

    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup


def test_kafka_config_missing_section(dummy_config):
    cfg_path = dummy_config(["[fleeble]"])
    path_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    config.__kafka_config = None
    with pytest.raises(ConfigError) as e:
        config.KafkaConfig()
    assert "Error parsing config file: section kafka not found" in str(e.value)
    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup


def test_config_bad_parsing(dummy_config, dummy_auth_token):
    cfg_path = dummy_config(["nope"])
    path_backup = os.environ.get('FEEDS_CONFIG')
    os.environ['FEEDS_CONFIG'] = cfg_path
    config.__config = None
    with pytest.raises(ConfigError) as e:
        config.FeedsConfig()
    assert "Error parsing config file {}:".format(cfg_path) in str(e.value)
    if path_backup is not None:
        os.environ['FEEDS_CONFIG'] = path_backup
