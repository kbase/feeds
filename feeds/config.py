import os
import configparser
from .exceptions import ConfigError

DEFAULT_CONFIG_PATH = "deploy.cfg"
ENV_CONFIG_PATH = "FEEDS_CONFIG"
ENV_CONFIG_BACKUP = "KB_DEPLOYMENT_CONFIG"
ENV_AUTH_TOKEN = "AUTH_TOKEN"

FEEDS_SECTION = "feeds"

KEY_DB_HOST = "db-host"
KEY_DB_PORT = "db-port"
KEY_DB_USER = "db-user"
KEY_DB_PW = "db-pw"
KEY_DB_NAME = "db-name"
KEY_DB_ENGINE = "db-engine"
KEY_GLOBAL_FEED = "global-feed"
KEY_DEBUG = "debug"
KEY_LIFESPAN = "lifespan"
KEY_AUTH_URL = "auth-url"
KEY_NJS_URL = "njs-url"
KEY_GROUPS_URL = "groups-url"
KEY_WS_URL = "workspace-url"
KEY_NMS_URL = "nms-url"
KEY_DEFAULT_COUNT = "default-note-count"
KEY_USE_KAFKA = "use-kafka"

KAFKA_SECTION = "kafka"
KEY_KAFKA_HOST = "host"
KEY_KAFKA_TOPICS = "topics"
KEY_KAFKA_GROUP_ID = "group-id"


class ConfigFileLoader(object):
    def __init__(self):
        config_file = self._find_config_path()
        self.cfg = self._load_config(config_file)

    def has_section(self, section: str) -> bool:
        return self.cfg.has_section(section)

    def get_line(self, section: str, key: str, required: bool=True) -> str:
        """
        A little wrapper that raises a ConfigError if a required key isn't present.
        """
        val = None
        try:
            val = self.cfg.get(section, key)
        except configparser.NoOptionError:
            if required:
                raise ConfigError("Required option {} not found in config section "
                                  "{}".format(key, section))
        if not val and required:
            raise ConfigError("Required option {} has no value!".format(key))
        return val

    def _find_config_path(self):
        """
        A little helper to test whether a given file path, or one given by an
        environment variable, exists.
        """
        for env in [ENV_CONFIG_PATH, ENV_CONFIG_BACKUP]:
            env_path = os.environ.get(env)
            if env_path:
                if not os.path.isfile(env_path):
                    raise ConfigError(
                        "Environment variable {} is set to {}, "
                        "which is not a config file.".format(ENV_CONFIG_PATH, env_path)
                    )
                else:
                    return env_path
        if not os.path.isfile(DEFAULT_CONFIG_PATH):
            raise ConfigError(
                "Unable to find config file - can't start server. Either set the {} or {} "
                "environment variable to a path, or copy 'deploy.cfg.example' to "
                "'deploy.cfg'".format(ENV_CONFIG_PATH, ENV_CONFIG_BACKUP)
            )
        return DEFAULT_CONFIG_PATH

    def _load_config(self, cfg_file):
        config = configparser.ConfigParser()
        with open(cfg_file, "r") as cfg:
            try:
                config.read_file(cfg)
            except configparser.Error as e:
                raise ConfigError("Error parsing config file {}: {}".format(cfg_file, e))
        return config


class FeedsConfig(object):
    """
    Loads a config set from the root deploy.cfg file. This should be in ini format.

    Keys of note are:
    """

    def __init__(self):
        # Look for the file. ENV_CONFIG_PATH > ENV_CONFIG_BACKUP > DEFAULT_CONFIG_PATH
        self.auth_token = os.environ.get(ENV_AUTH_TOKEN)
        if self.auth_token is None:
            raise RuntimeError("The AUTH_TOKEN environment variable must be set!")
        cfg = ConfigFileLoader()
        if not cfg.has_section(FEEDS_SECTION):
            raise ConfigError(
                "Error parsing config file: section {} not found!".format(FEEDS_SECTION)
            )
        self.db_engine = cfg.get_line(FEEDS_SECTION, KEY_DB_ENGINE)
        self.db_host = cfg.get_line(FEEDS_SECTION, KEY_DB_HOST)
        try:
            self.db_port = cfg.get_line(FEEDS_SECTION, KEY_DB_PORT)
            self.db_port = int(self.db_port)
            assert self.db_port > 0
        except (ValueError, AssertionError):
            raise ConfigError("{} must be an int > 0! Got {}".format(KEY_DB_PORT, self.db_port))
        self.db_user = cfg.get_line(FEEDS_SECTION, KEY_DB_USER, required=False)
        self.db_pw = cfg.get_line(FEEDS_SECTION, KEY_DB_PW, required=False)
        self.db_name = cfg.get_line(FEEDS_SECTION, KEY_DB_NAME, required=False)
        self.global_feed = cfg.get_line(FEEDS_SECTION, KEY_GLOBAL_FEED)
        self.global_feed_type = "user"  # doesn't matter, need a valid Entity type...
        try:
            self.lifespan = cfg.get_line(FEEDS_SECTION, KEY_LIFESPAN)
            self.lifespan = int(self.lifespan)
            assert self.lifespan > 0
        except (ValueError, AssertionError):
            raise ConfigError("{} must be an int > 0! Got {}".format(KEY_LIFESPAN, self.lifespan))
        self.debug = cfg.get_line(FEEDS_SECTION, KEY_DEBUG, required=False)
        if not self.debug or self.debug.lower() != "true":
            self.debug = False
        else:
            self.debug = True
        self.auth_url = cfg.get_line(FEEDS_SECTION, KEY_AUTH_URL)
        self.njs_url = cfg.get_line(FEEDS_SECTION, KEY_NJS_URL)
        self.ws_url = cfg.get_line(FEEDS_SECTION, KEY_WS_URL)
        self.groups_url = cfg.get_line(FEEDS_SECTION, KEY_GROUPS_URL)
        self.nms_url = cfg.get_line(FEEDS_SECTION, KEY_NMS_URL)
        self.default_max_notes = cfg.get_line(FEEDS_SECTION, KEY_DEFAULT_COUNT)
        try:
            self.default_max_notes = cfg.get_line(FEEDS_SECTION, KEY_DEFAULT_COUNT)
            self.default_max_notes = int(self.default_max_notes)
            assert self.default_max_notes > 0
        except (ValueError, AssertionError):
            raise ConfigError(
                "{} must be an int > 0! Got {}".format(KEY_DEFAULT_COUNT, self.default_max_notes)
            )


class KafkaConfig(object):
    def __init__(self):
        cfg = ConfigFileLoader()
        if not cfg.has_section(KAFKA_SECTION):
            raise ConfigError(
                "Error parsing config file: section {} not found!".format(KAFKA_SECTION)
            )
        self.kafka_host = cfg.get_line(KAFKA_SECTION, KEY_KAFKA_HOST)
        self.kafka_group_id = cfg.get_line(KAFKA_SECTION, KEY_KAFKA_GROUP_ID)
        self.kafka_topics = cfg.get_line(KAFKA_SECTION, KEY_KAFKA_TOPICS).split(",")


__config = None
__kafka_config = None


def get_config():
    global __config
    if not __config:
        __config = FeedsConfig()
    return __config


def get_kafka_config():
    global __kafka_config
    if not __kafka_config:
        __kafka_config = KafkaConfig()
    return __kafka_config
