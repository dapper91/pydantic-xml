"""
pydantic xml serialization/deserialization extension
"""

from . import config, errors
from .errors import ModelError
from .model import BaseXmlModel, XmlAttributeInfo, XmlElementInfo, XmlWrapperInfo, attr, element, wrapped
from .serializers import DEFAULT_ENCODER, XmlEncoder
