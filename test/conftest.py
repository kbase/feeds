import os
import configparser
import pytest
import tempfile

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

@pytest.fixture
def app():
    from feeds.server import create_app
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True
    })

    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

