import os
import configparser

def pytest_sessionstart(session):
    os.environ['AUTH_TOKEN'] = 'foo'
    os.environ['FEEDS_CONFIG'] = os.path.join(os.path.dirname(__file__), 'test.cfg')

def pytest_sessionfinish(session, exitstatus):
    pass

def test_config():
    """
    Returns a ConfigParser.
    Because I'm lazy.
    """
    cfg = configparser.ConfigParser()
    with open(os.environ['FEEDS_CONFIG'], 'r') as f:
        cfg.read_file(f)
    return cfg