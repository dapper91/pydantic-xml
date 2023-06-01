import abc
import dataclasses as dc
import typing
from enum import IntEnum
from inspect import isclass
from types import UnionType
from typing import Any, Dict, Optional, Tuple, Type, Union

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml.element import SearchMode, XmlElementReader, XmlElementWriter
from pydantic_xml.typedefs import NsMap

from . import factories
from .encoder import XmlEncoder


class Location(IntEnum):
    """
    Field data location.
    """

    MISSING = 0  # field location is not provided
    ELEMENT = 1  # field data is located at xml element
    ATTRIBUTE = 2  # field data is located at xml attribute
    WRAPPED = 3  # field data is wrapped by an element


class PydanticShapeType(IntEnum):
    """
    Pydantic shape type.
    """

    UNKNOWN = 0
    SCALAR = 1
    HOMOGENEOUS = 2
    HETEROGENEOUS = 3
    MAPPING = 4

    __SHAPE_TYPES__: Dict[int, int] = {
        pd.fields.SHAPE_SINGLETON:      SCALAR,

        pd.fields.SHAPE_LIST:           HOMOGENEOUS,
        pd.fields.SHAPE_SET:            HOMOGENEOUS,
        pd.fields.SHAPE_TUPLE_ELLIPSIS: HOMOGENEOUS,
        pd.fields.SHAPE_SEQUENCE:       HOMOGENEOUS,
        pd.fields.SHAPE_ITERABLE:       HOMOGENEOUS,
        pd.fields.SHAPE_FROZENSET:      HOMOGENEOUS,
        pd.fields.SHAPE_DEQUE:          HOMOGENEOUS,

        pd.fields.SHAPE_TUPLE:          HETEROGENEOUS,

        pd.fields.SHAPE_MAPPING:        MAPPING,
        pd.fields.SHAPE_DICT:           MAPPING,
        pd.fields.SHAPE_DEFAULTDICT:    MAPPING,

        pd.fields.SHAPE_GENERIC:        UNKNOWN,
    }

    @classmethod
    def from_shape(cls, shape: int) -> 'PydanticShapeType':
        return cls(cls.__SHAPE_TYPES__.get(shape, cls.UNKNOWN))


def is_xml_model(tp: Any) -> bool:
    return isclass(tp) and issubclass(tp, pxml.BaseXmlModel)


def is_union(type_: Any) -> bool:
    return typing.get_origin(type_) in [Union, UnionType]


def is_optional(type_: Any) -> bool:
    if not is_union(type_):
        return False

    union_args = typing.get_args(type_)
    if len(union_args) != 2:
        return False

    return type(None) in union_args


class Serializer(abc.ABC):
    """
    Base field serializer/deserializer.
    """

    @dc.dataclass(frozen=True)
    class Context:
        search_mode: SearchMode
        parent_is_root: bool = False
        parent_ns: Optional[str] = None
        parent_nsmap: Optional[NsMap] = None

    @abc.abstractmethod
    def serialize(self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False) -> Any:
        """
        Serializes a value into an xml element.

        :param element: element serialized value should be added to
        :param value: value to be serialized
        :param encoder: xml encoder to be used to serialize the value
        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text, Nones)
        """

    @abc.abstractmethod
    def deserialize(self, element: Optional[XmlElementReader]) -> Any:
        """
        Deserializes a value from an xml element.

        :param element: element deserialized value should be fetched from
        :return: deserialized value
        """

    @classmethod
    def _get_field_location(cls, field_info: pd.fields.FieldInfo) -> Location:
        if isinstance(field_info, pxml.XmlElementInfo):
            field_location = Location.ELEMENT
        elif isinstance(field_info, pxml.XmlAttributeInfo):
            field_location = Location.ATTRIBUTE
        elif isinstance(field_info, pxml.XmlWrapperInfo):
            field_location = Location.WRAPPED
        else:
            field_location = Location.MISSING

        return field_location

    @classmethod
    def _get_entity_info(
            cls,
            model_field: pd.fields.ModelField,
    ) -> Tuple[Optional[str], Optional[str], Optional[NsMap]]:
        field_info = model_field.field_info

        if isinstance(field_info, pxml.XmlElementInfo):
            return field_info.tag, field_info.ns, field_info.nsmap
        elif isinstance(field_info, pxml.XmlAttributeInfo):
            return field_info.name, field_info.ns, None
        elif isinstance(field_info, pxml.XmlWrapperInfo):
            return field_info.path, field_info.ns, field_info.nsmap
        else:
            return None, None, None

    @classmethod
    def _build_field_serializer(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            ctx: Context,
    ) -> 'Serializer':
        field_type = model_field.type_
        field_info = model_field.field_info

        shape_type = PydanticShapeType.from_shape(model_field.shape)
        if shape_type is PydanticShapeType.UNKNOWN:
            raise TypeError(f"fields of type {model_field.type_} are not supported")

        if is_xml_model(field_type):
            is_model_field = True
        else:
            is_model_field = False

        is_union_type = is_union(model_field.outer_type_) and not is_optional(model_field.outer_type_)

        field_location = cls._get_field_location(field_info)

        if field_location is Location.WRAPPED:
            return factories.WrappedSerializerFactory.build(model, model_field, ctx)
        elif is_union_type:
            return factories.UnionSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.SCALAR and not is_model_field:
            return factories.PrimitiveTypeSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.SCALAR and is_model_field:
            return factories.ModelSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.MAPPING:
            return factories.MappingSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.HOMOGENEOUS:
            return factories.HomogeneousSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.HETEROGENEOUS:
            return factories.HeterogeneousSerializerFactory.build(model, model_field, field_location, ctx)
        else:
            raise AssertionError("unreachable")
