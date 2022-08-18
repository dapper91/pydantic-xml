import distutils.util
import os

REGISTER_NS_PREFIXES = distutils.util.strtobool(os.environ.get('REGISTER_NS_PREFIXES', 'true'))
FORCE_STD_XML = distutils.util.strtobool(os.environ.get('FORCE_STD_XML', 'false'))
