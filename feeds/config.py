import os
import configparser
from .exceptions import ConfigError

DEFAULT_CONFIG_PATH = "deploy.cfg"
ENV_CONFIG_PATH = "FEEDS_CONFIG"
ENV_CONFIG_BACKUP = "KB_DEPLOYMENT_CONFIG"
ENV_AUTH_TOKEN = "AUTH_TOKEN"

INI_SECTION = "feeds"
DB_HOST = "redis-host"
DB_HOST_PORT = "redis-port"
DB_USER = "redis-user"
DB_PW = "redis-pw"
DB_DB = "redis-db"
AUTH_URL = "auth-url"
ADMIN_LIST = "admins"
GLOBAL_FEED = "global-feed"


class FeedsConfig(object):
    """
    Loads a config set from the root deploy.cfg file. This should be in ini format.

    Keys of note are:

    redis-host
    redis-port
    redis-user
    redis-pw
    auth-url
    global-feed - name of the feed to represent a global user, or
        notifications that everyone should see.
    """

    def __init__(self):
        # Look for the file. ENV_CONFIG_PATH > ENV_CONFIG_BACKUP > DEFAULT_CONFIG_PATH
        self.auth_token = os.environ.get(ENV_AUTH_TOKEN)
        if self.auth_token is None:
            raise RuntimeError("The AUTH_TOKEN environment variable must be set!")
        config_file = self._find_config_path()
        cfg = self._load_config(config_file)
        if not cfg.has_section(INI_SECTION):
            raise ConfigError(
                "Error parsing config file: section {} not found!".format(INI_SECTION)
            )
        self.redis_host = self._get_line(cfg, DB_HOST)
        self.redis_port = self._get_line(cfg, DB_HOST_PORT)
        self.redis_user = self._get_line(cfg, DB_USER, required=False)
        self.redis_pw = self._get_line(cfg, DB_PW, required=False)
        self.redis_db = self._get_line(cfg, DB_DB, required=False)
        if self.redis_db is None:
            self.redis_db = 0
        self.global_feed = self._get_line(cfg, GLOBAL_FEED)
        self.auth_url = self._get_line(cfg, AUTH_URL)
        self.admins = self._get_line(cfg, ADMIN_LIST).split(",")

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

    def _get_line(self, config, key, required=True):
        """
        A little wrapper that raises a ConfigError if a required key isn't present.
        """
        val = None
        try:
            val = config.get(INI_SECTION, key)
        except configparser.NoOptionError:
            if required:
                raise ConfigError("Required option {} not found in config".format(key))
        if not val and required:
            raise ConfigError("Required option {} has no value!".format(key))
        return val


__config = None


def get_config():
    global __config
    if not __config:
        __config = FeedsConfig()
    return __config
