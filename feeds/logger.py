import logging
import traceback

def get_log(name):
    return logging.getLogger(__name__)


def log(name, msg, *args, level=logging.INFO):
    get_log(name).log(level, msg, *args)


def log_error(name, error):
    formatted_error = ''.join(
        traceback.format_exception(
            etype=type(error),
            value=error,
            tb=error.__traceback__)
        )
    log(name, "Exception: " + formatted_error, level=logging.ERROR)
