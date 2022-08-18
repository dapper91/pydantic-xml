import abc
import dataclasses as dc
import datetime as dt
from copy import deepcopy
from decimal import Decimal
from enum import IntEnum
from inspect import isclass
from typing import Any, Dict, List, Mapping, Optional, Sized, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors

from .backend import etree
from .utils import NsMap, QName, merge_nsmaps


class XmlEncoder:
    """
    Xml data encoder.
    """

    def encode(self, obj: Any) -> str:
        """
        Encodes provided object into a string

        :param obj: object to be encoded
        :return: encoded object
        """

        if isinstance(obj, str):
            return obj
        if isinstance(obj, (int, float, Decimal)):
            return str(obj)
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, (dt.datetime, dt.date, dt.time)):
            return obj.isoformat()

        return self.default(obj)

    def default(self, obj: Any) -> str:
        raise TypeError(f'Object of type {obj.__class__.__name__} is not XML serializable')


DEFAULT_ENCODER = XmlEncoder()


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


def find_element_or_create(root: etree.Element, name: str) -> etree.Element:
    if (sub_element := root.find(name)) is None:
        sub_element = etree.SubElement(root, name)

    return sub_element


class Serializer(abc.ABC):
    """
    Base field serializer/deserializer.
    """

    @dc.dataclass(frozen=True)
    class Context:
        parent_is_root: bool = False
        parent_ns: Optional[str] = None
        parent_nsmap: Optional[NsMap] = None

        entity_name: Optional[str] = None
        entity_ns: Optional[str] = None
        entity_nsmap: Optional[NsMap] = None

    @abc.abstractmethod
    def serialize(self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False) -> Any:
        """
        Serializes a value into an xml element.

        :param element: element serialized value should be added to
        :param value: value to be serialized
        :param encoder: xml encoder to be used to serialize the value
        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text, Nones)
        """

    @abc.abstractmethod
    def deserialize(self, root: etree.Element) -> Any:
        """
        Deserializes a value from an xml element.

        :param root: element deserialized value should be fetched to
        :return: deserialized value
        """

    @classmethod
    def build_field_serializer(
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

        if isclass(field_type) and issubclass(field_type, pxml.BaseXmlModel):
            is_model_field = True
        else:
            is_model_field = False

        if isinstance(field_info, pxml.XmlElementInfo):
            field_location = Location.ELEMENT
            ctx = dc.replace(ctx, entity_name=field_info.tag, entity_ns=field_info.ns, entity_nsmap=field_info.nsmap)
        elif isinstance(field_info, pxml.XmlAttributeInfo):
            field_location = Location.ATTRIBUTE
            ctx = dc.replace(ctx, entity_name=field_info.name, entity_ns=field_info.ns)
        elif isinstance(field_info, pxml.XmlWrapperInfo):
            field_location = Location.WRAPPED
            ctx = dc.replace(ctx, entity_name=field_info.path, entity_ns=field_info.ns, entity_nsmap=field_info.nsmap)
        else:
            field_location = Location.MISSING

        if field_location is Location.WRAPPED:
            return WrappedSerializerFactory.build(model, model_field, ctx)
        elif shape_type is PydanticShapeType.SCALAR and not is_model_field:
            return PrimitiveTypeSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.SCALAR and is_model_field:
            return ModelSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.MAPPING:
            return MappingSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.HOMOGENEOUS:
            return HomogeneousSerializerFactory.build(model, model_field, field_location, ctx)
        elif shape_type is PydanticShapeType.HETEROGENEOUS:
            return HeterogeneousSerializerFactory.build(model, model_field, field_location, ctx)
        else:
            raise AssertionError("unreachable")


class PrimitiveTypeSerializerFactory:
    """
    Primitive type serializer factory.
    """

    class TextSerializer(Serializer):
        def serialize(
                self,  element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)
            element.text = encoded
            return element

        def deserialize(self, element: etree.Element) -> Optional[str]:
            return element.text

    class AttributeSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            ns_attrs = model.__xml_ns_attrs__
            name = ctx.entity_name or model_field.name
            ns = ctx.entity_ns or (ctx.parent_ns if ns_attrs else None)
            nsmap = ctx.parent_nsmap

            self.attr_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)
            element.set(self.attr_name, encoded)

            return element

        def deserialize(self, element: etree.Element) -> Optional[str]:
            return element.get(self.attr_name)

    class ElementSerializer(Serializer):
        def __init__(self, model_field: pd.fields.ModelField, ctx: Serializer.Context):
            name = ctx.entity_name or model_field.name
            ns = ctx.entity_ns or ctx.parent_ns
            nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)

            if (sub_element := element.find(self.element_name)) is None:
                sub_element = etree.SubElement(element, self.element_name)

            sub_element.text = encoded
            return sub_element

        def deserialize(self, element: etree.Element) -> Any:
            return element.findtext(self.element_name)

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            return cls.AttributeSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.TextSerializer()
        else:
            raise AssertionError("unreachable")


class ModelSerializerFactory:
    """
    Model serializer factory.
    """

    class BaseSerializer(Serializer, abc.ABC):
        def __init__(
                self,
                model_field: Optional[pd.fields.ModelField],
                model: Type['pxml.BaseXmlModel'],
                ctx: Serializer.Context,
        ):
            field_name = model_field.name if model_field else None
            name = ctx.entity_name or model.__xml_tag__ or field_name or model.__class__.__name__
            ns = ctx.entity_ns or model.__xml_ns__ or (ctx.parent_ns if model.__xml_inherit_ns__ else None)
            nsmap = merge_nsmaps(ctx.entity_nsmap, model.__xml_nsmap__, ctx.parent_nsmap)
            is_root = model.__custom_root_type__
            ctx = dc.replace(
                ctx,
                parent_ns=ns,
                parent_nsmap=nsmap,
                parent_is_root=is_root,
            )

            self.is_root = is_root
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
            self.field_serializers = {
                field_name: self.build_field_serializer(model, model_subfield, ctx)
                for field_name, model_subfield in model.__fields__.items()
            }

    class RootSerializer(BaseSerializer):
        def serialize(
                self, element: Optional[etree.Element], value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> etree.Element:
            if element is None:
                element = etree.Element(self.element_name)

            for field_name, field_serializer in self.field_serializers.items():
                field_serializer.serialize(element, getattr(value, field_name), encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: etree.Element) -> Any:
            result = {
                field_name: field_serializer.deserialize(element)
                for field_name, field_serializer in self.field_serializers.items()
            }
            if self.is_root:
                return result['__root__']
            else:
                return result

    class ElementSerializer(BaseSerializer):
        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            sub_element = etree.Element(self.element_name)

            for field_name, field_serializer in self.field_serializers.items():
                field_serializer.serialize(
                    sub_element, getattr(value, field_name), encoder=encoder, skip_empty=skip_empty,
                )

            if not skip_empty or sub_element.text or sub_element.attrib or len(sub_element) != 0:
                element.append(sub_element)
                return sub_element
            else:
                return None

        def deserialize(self, element: etree.Element) -> Optional[Dict[str, Any]]:
            if (sub_element := element.find(self.element_name)) is not None:
                result = {
                    field_name: field_serializer.deserialize(sub_element)
                    for field_name, field_serializer in self.field_serializers.items()
                }
                if self.is_root:
                    return result['__root__']
                else:
                    return result
            else:
                return None

    @classmethod
    def from_model(cls, model: Type['pxml.BaseXmlModel']) -> 'RootSerializer':
        return cls.RootSerializer(None, model, Serializer.Context(parent_is_root=True))

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        sub_model = model_field.type_
        ctx = dc.replace(
            ctx,
            parent_ns=ctx.parent_ns or model.__xml_ns__,
            parent_nsmap=merge_nsmaps(ctx.parent_nsmap, model.__xml_nsmap__),
        )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model_field, sub_model, ctx)
        elif not ctx.parent_is_root and field_location is Location.MISSING:
            return cls.ElementSerializer(model_field, sub_model, ctx)
        elif ctx.parent_is_root and field_location is Location.MISSING:
            return cls.RootSerializer(model_field, sub_model, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "attributes of model type are not supported",
            )
        else:
            raise AssertionError("unreachable")


class MappingSerializerFactory:
    """
    Mapping type serializer factory.
    """

    class BaseSerializer(Serializer, abc.ABC):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            name = ctx.entity_name or model_field.name

            self.parent_ns = ns = ctx.entity_ns or ctx.parent_ns
            self.parent_nsmap = nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
            self.ns_attrs = model.__xml_ns_attrs__

    class AttributesSerializer(BaseSerializer):
        def serialize(
                self, element: etree.Element, value: Mapping[str, Any], *, encoder: XmlEncoder, skip_empty: bool = False
        ) -> Optional[etree.Element]:
            if value is None:
                return element

            if skip_empty and len(value) == 0:
                return element

            if self.ns_attrs:
                ns = self.parent_nsmap.get(self.parent_ns) if self.parent_ns else None
                element.attrib.update({
                    QName(tag=attr, ns=ns).uri: encoder.encode(val)
                    for attr, val in value.items()
                })
            else:
                element.attrib.update({
                    attr: encoder.encode(val)
                    for attr, val in value.items()
                })

            return element

        def deserialize(self, element: etree.Element) -> Dict[str, str]:
            if self.ns_attrs:
                return {QName.from_uri(attr).tag: val for attr, val in element.attrib.items()}
            else:
                return {attr: val for attr, val in element.attrib.items()}

    class ElementSerializer(BaseSerializer):
        def serialize(
                self, element: etree.Element, value: Mapping[str, Any], *, encoder: XmlEncoder, skip_empty: bool = False
        ) -> etree.Element:
            if skip_empty and len(value) == 0:
                return element

            sub_element = find_element_or_create(element, self.element_name)
            if self.ns_attrs:
                ns = self.parent_nsmap.get(self.parent_ns) if self.parent_ns else None
                sub_element.attrib.update({
                    QName(tag=attr, ns=ns).uri: encoder.encode(val)
                    for attr, val in value.items()
                })
            else:
                sub_element.attrib.update({
                    attr: encoder.encode(val)
                    for attr, val in value.items()
                })

            return sub_element

        def deserialize(self, element: etree.Element) -> Optional[Dict[str, str]]:
            if (sub_element := element.find(self.element_name)) is not None:
                if self.ns_attrs:
                    return {
                        QName.from_uri(attr).tag: val
                        for attr, val in sub_element.attrib.items()
                    }
                else:
                    return {
                        attr: val
                        for attr, val in sub_element.attrib.items()
                    }
            else:
                return None

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        assert model_field.sub_fields is not None, "unexpected model field"
        value_field = model_field.sub_fields[0]
        value_type = value_field.type_
        if PydanticShapeType.from_shape(value_field.shape) is not PydanticShapeType.SCALAR:
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "mapping value should be of scalar type",
            )

        if isclass(value_type) and issubclass(value_type, pxml.BaseXmlModel):
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "mapping value types can't be models",
            )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.AttributesSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "attributes of mapping type are not supported",
            )
        else:
            raise AssertionError("unreachable")


class HomogeneousSerializerFactory:
    """
    Homogeneous collection type serializer factory.
    """

    class ElementSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            assert model_field.sub_fields is not None, "unexpected model field"

            name = ctx.entity_name or model_field.name
            ns = ctx.entity_ns or ctx.parent_ns
            nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)

            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
            self.serializer = self.build_field_serializer(
                model,
                model_field.sub_fields[0],
                dc.replace(
                    ctx,
                    parent_is_root=True,
                    parent_ns=ns,
                    parent_nsmap=nsmap,
                ),
            )

        def serialize(
                self, element: etree.Element, value: List[Any], *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return element

            if skip_empty and len(value) == 0:
                return element

            for val in value:
                sub_element = etree.SubElement(element, self.element_name)
                self.serializer.serialize(sub_element, val, encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: etree.Element) -> Optional[List[Any]]:
            return [
                self.serializer.deserialize(sub_element)
                for sub_element in element.findall(self.element_name)
            ]

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        is_root = model.__custom_root_type__

        assert model_field.sub_fields is not None, "unexpected model field"
        item_field = model_field.sub_fields[0]

        if PydanticShapeType.from_shape(item_field.shape) in (
            PydanticShapeType.HOMOGENEOUS,
            PydanticShapeType.HETEROGENEOUS,
        ):
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "collection elements can't be of collection type",
            )

        if is_root and field_location is Location.MISSING:
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "root model collections should be marked as elements",
            )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "attributes of collection type are not supported",
            )
        else:
            raise AssertionError("unreachable")


class HeterogeneousSerializerFactory:
    """
    Heterogeneous collection type serializer factory.
    """

    class ElementSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            assert model_field.sub_fields is not None, "unexpected model field"

            name = ctx.entity_name or model_field.name
            ns = ctx.entity_ns or ctx.parent_ns
            nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)

            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
            self.serializers = [
                self.build_field_serializer(
                    model,
                    sub_field,
                    dc.replace(
                        ctx,
                        parent_is_root=True,
                        parent_ns=ns,
                        parent_nsmap=nsmap,
                    ),
                )
                for sub_field in model_field.sub_fields
            ]

        def serialize(
                self, element: etree.Element, value: List[Any], *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return element

            if skip_empty and len(value) == 0:
                return element

            for serializer, val in zip(self.serializers, value):
                sub_element = etree.SubElement(element, self.element_name)
                serializer.serialize(sub_element, val, encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: etree.Element) -> Optional[List[Any]]:
            return [
                serializer.deserialize(sub_element)
                for serializer, sub_element in zip(self.serializers, element.findall(self.element_name))
            ]

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        is_root = model.__custom_root_type__

        assert model_field.sub_fields is not None, "unexpected model field"
        for item_field in model_field.sub_fields:
            if PydanticShapeType.from_shape(item_field.shape) in (
                PydanticShapeType.HOMOGENEOUS,
                PydanticShapeType.HETEROGENEOUS,
            ):
                raise errors.ModelFieldError(
                    model.__class__.__name__, model_field.name, "collection elements can't be of collection type",
                )

            if is_root and field_location is Location.MISSING:
                raise errors.ModelFieldError(
                    model.__class__.__name__, model_field.name, "root model collections should be marked as elements",
                )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__class__.__name__, model_field.name, "attributes of collection type are not supported",
            )
        else:
            raise AssertionError("unreachable")


class WrappedSerializerFactory:
    """
    Wrapped serializer factory.
    """

    class ElementPathSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            path = ctx.entity_name
            ns = ctx.entity_ns or ctx.parent_ns
            nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)

            model_field = deepcopy(model_field)
            field_info = model_field.field_info

            assert path is not None, "path is not provided"
            assert isinstance(field_info, pxml.XmlWrapperInfo)
            model_field.field_info = field_info.entity or pd.fields.FieldInfo()

            self.path = tuple(QName.from_alias(tag=part, ns=ns, nsmap=nsmap).uri for part in path.split('/'))
            self.serializer = self.build_field_serializer(
                model,
                model_field,
                ctx=dc.replace(
                    ctx,
                    parent_is_root=True,
                    parent_ns=ns,
                    parent_nsmap=nsmap,
                ),
            )

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return element

            if skip_empty and isinstance(value, Sized) and len(value) == 0:
                return element

            for part in self.path:
                element = find_element_or_create(element, part)

            self.serializer.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: etree.Element) -> Optional[Any]:
            if (sub_element := element.find('/'.join(self.path))) is not None:
                return self.serializer.deserialize(sub_element)
            else:
                return None

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        return cls.ElementPathSerializer(model, model_field, ctx)
