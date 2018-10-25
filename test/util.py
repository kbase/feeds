import uuid

def assert_is_uuid(s):
    # raises a ValueError if not. Good enough for testing.
    uuid.UUID(s)