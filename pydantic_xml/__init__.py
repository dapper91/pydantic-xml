"""
pydantic xml serialization/deserialization extension
"""

from . import config, errors, model
from .errors import ModelError, ParsingError
from .fields import XmlFieldSerializer, XmlFieldValidator, attr, computed_attr, computed_element, element, wrapped
from .fields import xml_field_serializer, xml_field_validator
from .model import BaseXmlModel, RootXmlModel, create_model

__all__ = (
    'BaseXmlModel',
    'RootXmlModel',
    'ModelError',
    'ParsingError',
    'attr',
    'element',
    'wrapped',
    'computed_attr',
    'computed_element',
    'create_model',
    'errors',
    'model',
    'xml_field_serializer',
    'xml_field_validator',
    'XmlFieldValidator',
    'XmlFieldSerializer',
)
