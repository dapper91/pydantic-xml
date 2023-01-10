import os


def strtobool(val: str) -> bool:
    """
    Converts a string representation of boolean type to true or false.
    """

    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError


REGISTER_NS_PREFIXES = strtobool(os.environ.get('REGISTER_NS_PREFIXES', 'true'))
FORCE_STD_XML = strtobool(os.environ.get('FORCE_STD_XML', 'false'))
