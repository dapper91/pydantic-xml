"""
pydantic xml serialization/deserialization extension
"""

from . import config, errors
from .errors import ModelError
from .model import BaseGenericXmlModel, BaseXmlModel, XmlAttributeInfo, XmlElementInfo, XmlWrapperInfo, attr, element
from .model import wrapped
from .serializers import DEFAULT_ENCODER, XmlEncoder
