import logging


def get_log(name):
    return logging.getLogger(__name__)


def log(name, msg, *args, level=logging.INFO):
    logging.getLogger(__name__).log(level, msg, *args)


def log_error(name, error):
    log(name, "Exception: " + str(error) + error, level=logging.ERROR)
