import pytest
from feeds.util import epoch_ms

def test_epoch_ms():
    '''
    Just make sure it's an int with 13 digits. Be more rigorous later. At least, before year 2287.
    '''
    t = epoch_ms()
    assert len(str(t)) == 13