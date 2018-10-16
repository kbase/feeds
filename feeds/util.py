import requests
import time

def check_user_id(user_id):
    """
    Test to see if a user id is real.
    Returns True if so, False if not.
    """
    pass

def check_user_ids(id_list):
    """
    Test to see if user ids are all real.
    Returns True if so, a list of invalid names if not.
    """
    pass

def epoch_ms():
    return int(round(time.time()*1000))