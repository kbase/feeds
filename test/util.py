import uuid

def validate_uuid(test_uuid):
    """
    test_uuid should be a UUID object
    """
    test_str = str(test_uuid)
    try:
        val = uuid.UUID(test_str, version=4)
    except ValueError:
        return False

    return test_str == str(val)