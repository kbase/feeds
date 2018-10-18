class ConfigError(Exception):
    """
    Raised when there's a problem with the service configuration.
    """
    pass

class MissingVerbError(Exception):
    """
    Raised when trying to convert from string -> registered verb, but the string's wrong.
    """
    pass