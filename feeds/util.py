from datetime import datetime


def epoch_ms():
    return int(datetime.utcnow().timestamp() * 1000)
