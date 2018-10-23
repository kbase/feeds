import redis
from feeds.config import get_config

connection_pool = None


def get_redis_connection(server_name='default'):
    '''
    Gets the specified redis connection
    '''
    global connection_pool

    if connection_pool is None:
        connection_pool = setup_redis()

    return redis.StrictRedis(connection_pool=connection_pool)


def setup_redis():
    '''
    Starts the connection pool for the configured redis server
    '''
    config = get_config()
    pool = redis.ConnectionPool(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_pw,
        db=config.redis_db

        # decode_responses=config.get('decode_responses', True),
        # # connection options
        # socket_timeout=config.get('socket_timeout', None),
        # socket_connect_timeout=config.get('socket_connect_timeout', None),
        # socket_keepalive=config.get('socket_keepalive', False),
        # socket_keepalive_options=config.get('socket_keepalive_options', None),
        # retry_on_timeout=config.get('retry_on_timeout', False),
    )
    return pool
