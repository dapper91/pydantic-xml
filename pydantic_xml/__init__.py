"""
pydantic xml serialization/deserialization extension
"""

from . import config, errors, model
from .errors import ModelError, ParsingError
from .model import BaseXmlModel, RootXmlModel, XmlFieldSerializer, XmlFieldValidator, attr, computed_attr
from .model import computed_element, create_model, element, wrapped, xml_field_serializer, xml_field_validator

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
