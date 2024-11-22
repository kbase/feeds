import os
import configparser
from .exceptions import ConfigError

DEFAULT_CONFIG_PATH = "deploy.cfg"
ENV_CONFIG_PATH = "FEEDS_CONFIG"
ENV_CONFIG_BACKUP = "KB_DEPLOYMENT_CONFIG"
ENV_AUTH_TOKEN = "AUTH_TOKEN"

INI_SECTION = "feeds"

KEY_DB_HOST = "db-host"
KEY_DB_PORT = "db-port"
KEY_DB_USER = "db-user"
KEY_DB_PW = "db-pw"
KEY_DB_NAME = "db-name"
KEY_DB_ENGINE = "db-engine"
KEY_DB_RETRYWRITES = "db-retrywrites"
KEY_GLOBAL_FEED = "global-feed"
KEY_DEBUG = "debug"
KEY_LIFESPAN = "lifespan"
KEY_AUTH_URL = "auth-url"
KEY_NJS_URL = "njs-url"
KEY_GROUPS_URL = "groups-url"
KEY_WS_URL = "workspace-url"
KEY_NMS_URL = "nms-url"
KEY_DEFAULT_COUNT = "default-note-count"
KEY_SERVICE_GROUPS = "service-groups"
KEY_SERVICE_WORKSPACE = "service-workspace"
KEY_SERVICE_NARRATIVE = "service-narrative"
KEY_SERVICE_JOBS = "service-jobs"
KEY_SERVICE_KBASE = "service-kbase"


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
        config_file = self._find_config_path()
        cfg = self._load_config(config_file)
        if not cfg.has_section(INI_SECTION):
            raise ConfigError(
                "Error parsing config file: section {} not found!".format(INI_SECTION)
            )
        self.db_engine = self._get_line(cfg, KEY_DB_ENGINE)
        self.db_host = self._get_line(cfg, KEY_DB_HOST)
        try:
            self.db_port = self._get_line(cfg, KEY_DB_PORT)
            self.db_port = int(self.db_port)
            assert self.db_port > 0
        except (ValueError, AssertionError):
            raise ConfigError("{} must be an int > 0! Got {}".format(KEY_DB_PORT, self.db_port))
        self.db_user = self._get_line(cfg, KEY_DB_USER, required=False)
        self.db_pw = self._get_line(cfg, KEY_DB_PW, required=False)
        self.db_name = self._get_line(cfg, KEY_DB_NAME, required=False)
        self.db_retrywrites = self._get_line(cfg, KEY_DB_RETRYWRITES, required=False) == "true"
        self.global_feed = self._get_line(cfg, KEY_GLOBAL_FEED)
        self.global_feed_type = "user"  # doesn't matter, need a valid Entity type...
        try:
            self.lifespan = self._get_line(cfg, KEY_LIFESPAN)
            self.lifespan = int(self.lifespan)
            assert self.lifespan > 0
        except (ValueError, AssertionError):
            raise ConfigError("{} must be an int > 0! Got {}".format(KEY_LIFESPAN, self.lifespan))
        self.debug = self._get_line(cfg, KEY_DEBUG, required=False)
        if not self.debug or self.debug.lower() != "true":
            self.debug = False
        else:
            self.debug = True

        # URLs
        self.auth_url = self._get_line(cfg, KEY_AUTH_URL)
        self.njs_url = self._get_line(cfg, KEY_NJS_URL)
        self.ws_url = self._get_line(cfg, KEY_WS_URL)
        self.groups_url = self._get_line(cfg, KEY_GROUPS_URL)
        self.nms_url = self._get_line(cfg, KEY_NMS_URL)

        # Source service names
        self.service_groups = self._get_line(cfg, KEY_SERVICE_GROUPS)
        self.service_workspace = self._get_line(cfg, KEY_SERVICE_WORKSPACE)
        self.service_narrative = self._get_line(cfg, KEY_SERVICE_NARRATIVE)
        self.service_jobs = self._get_line(cfg, KEY_SERVICE_JOBS)
        self.service_kbase = self._get_line(cfg, KEY_SERVICE_KBASE)

        self.default_max_notes = self._get_line(cfg, KEY_DEFAULT_COUNT)
        try:
            self.default_max_notes = self._get_line(cfg, KEY_DEFAULT_COUNT)
            self.default_max_notes = int(self.default_max_notes)
            assert self.default_max_notes > 0
        except (ValueError, AssertionError):
            raise ConfigError(
                "{} must be an int > 0! Got {}".format(KEY_DEFAULT_COUNT, self.default_max_notes)
            )

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


def get_config(from_disk=False):
    global __config
    if not __config:
        __config = FeedsConfig()
    return __config
