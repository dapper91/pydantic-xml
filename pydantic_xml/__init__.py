"""
pydantic xml serialization/deserialization extension
"""

from . import config, errors, model
from .errors import ModelError, ParsingError
from .model import BaseXmlModel, RootXmlModel, UnboundHandler, attr, computed_attr, computed_element, element
from .model import unbound_handler, wrapped

__all__ = (
    'BaseXmlModel',
    'RootXmlModel',
    'ModelError',
    'ParsingError',
    'UnboundHandler',
    'attr',
    'element',
    'wrapped',
    'unbound_handler',
    'computed_attr',
    'computed_element',
    'errors',
    'model',
)
