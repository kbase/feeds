from requests import HTTPError

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

class InvalidTokenError(Exception):
    """
    Raised when finding out that a user or service auth token is invalid.
    Wraps HTTPError.
    """
    def __init__(self, msg=None, http_error=None):
        if msg is None:
            msg = "Invalid token."
        super(InvalidTokenError, self).__init__(msg)
        self.http_error = http_error

class TokenLookupError(Exception):
    """
    Raised when having problems looking up an auth token. Wraps HTTPError.
    """
    def __init__(self, msg=None, http_error=None):
        if msg is None:
            msg = "Unable to look up token information."
        super(TokenLookupError, self).__init__(msg)
        self.http_error = http_error

class InvalidActorError(Exception):
    """
    Raised when an actor doesn't exist in the system as either a user or Group.
    """
    pass

class MissingTokenError(Exception):
    """
    Raised when a request header doesn't have a token, but needs one.
    """
    pass