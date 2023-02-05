"""
pydantic xml serialization/deserialization extension
"""

from . import config, errors
from .errors import ModelError, ParsingError
from .model import BaseGenericXmlModel, BaseXmlModel, XmlAttributeInfo, XmlElementInfo, XmlWrapperInfo, attr, element
from .model import wrapped
from .serializers import DEFAULT_ENCODER, XmlEncoder

__all__ = (
    'BaseXmlModel',
    'BaseGenericXmlModel',
    'XmlEncoder',
    'DEFAULT_ENCODER',
    'ModelError',
    'XmlAttributeInfo',
    'XmlElementInfo',
    'XmlWrapperInfo',
    'ParsingError',
    'attr',
    'element',
    'wrapped',
    'errors',
)
