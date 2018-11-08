import os
import tempfile

import pytest

@pytest.mark.parametrize('path', (
    '/api/V1/notifications',
))
def test_get_notifications(client, path):
    response = client.get(path)
    print(response)
