"""
This module handles authentication management. This mainly means:
* validating auth tokens
* validating user ids
"""

from .config import config
import requests
import json
from .exceptions import (
    InvalidTokenError,
    TokenLookupError
)
from .util import epoch_ms
from cachetools import (
    Cache,
    TTLCache
)
AUTH_URL = config.auth_url
AUTH_API_PATH = '/api/V2/'
CACHE_EXPIRE_TIME = 300  # seconds

class TokenCache(TTLCache):
    """
    Extends the TTLCache to handle KBase auth tokens.
    So they have a base expiration of 5 minutes,
    but expire sooner if the token itself expires.
    """
    def __getitem__(self, key, cache_getitem=Cache.__getitem__):
        token = super(TokenCache, self).__getitem__(key, cache_getitem=cache_getitem)
        if token.get('expires', 0) < epoch_ms():
            return self.__missing__(key)
        else:
            return token

__token_cache = TokenCache(1000, CACHE_EXPIRE_TIME)

def validate_service_token(token):
    """
    Validates a service token. If valid, and of type Service, returns the token name.
    If invalid, raises an InvalidTokenError. If any other errors occur, raises
    a TokenLookupError.

    TODO: I know this is going to be rife with issues. The name of the token doesn't have
    to be the service. But as long as it's a Service token, then it came from in KBase, so
    everything should be ok.
    TODO: Add 'source' to PUT notification endpoint.
    """
    token = __fetch_token(token)
    if token.get('type') == 'Service':
        return token.get('name')
    else:
        raise InvalidTokenError("Token is not a Service token!")

def valid_user_token(token):
    """
    Validates a user auth token.
    If valid, does nothing. If invalid, raises an InvalidTokenError.
    """
    __fetch_token(token)

def __fetch_token(token):
    """
    Returns token info from the auth server. Caches it locally for a while.
    If the token is invalid or there's any other auth problems, either
    an InvalidTokenError or TokenLookupError gets raised.
    """
    fetched = __token_cache.get(token)
    if fetched:
        return fetched
    else:
        try:
            r = __auth_request('token', token)
            token_info = json.loads(r.content)
            __token_cache[token] = token_info
            return token_info
        except requests.HTTPError as e:
            _handle_errors(e)

def __auth_request(path, token):
    """
    Makes a request of the auth server after cramming the token in a header.
    Only makes GET requests, since that's all we should need.
    """
    headers = {'Authorization', token}
    r = requests.get(AUTH_URL + AUTH_API_PATH + path, headers=headers)
    # the requests that fail based on the token (401, 403) get returned for the
    # calling function to turn into an informative error
    # others - 404, 500 - get raised
    r.raise_for_status()
    return r

def _handle_errors(err):
    if err.response.status_code == 401:
        err_content = json.loads(err.response.content)
        err_msg = err_content.get('error', {}).get('apperror', 'Invalid token')
        raise InvalidTokenError(msg=err_msg, http_error=err)
    else:
        raise TokenLookupError(http_error=err)
