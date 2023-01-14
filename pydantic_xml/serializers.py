import abc
import dataclasses as dc
import datetime as dt
import ipaddress
from copy import deepcopy
from decimal import Decimal
from enum import Enum, IntEnum
from inspect import isclass
from typing import Any, Dict, List, Optional, Sized, Tuple, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors

from .backend import create_element, etree
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
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, (int, float, Decimal)):
            return str(obj)
        if isinstance(obj, (dt.datetime, dt.date, dt.time)):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return self.encode(obj.value)
        if isinstance(
            obj, (
                ipaddress.IPv4Address,
                ipaddress.IPv6Address,
                ipaddress.IPv4Network,
                ipaddress.IPv6Network,
                ipaddress.IPv4Interface,
                ipaddress.IPv6Interface,
            ),
        ):
            return str(obj)

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


def is_xml_model(tp: Any) -> bool:
    return isclass(tp) and issubclass(tp, pxml.BaseXmlModel)


class Serializer(abc.ABC):
    """
    Base field serializer/deserializer.
    """

    @dc.dataclass(frozen=True)
    class Context:
        parent_is_root: bool = False
        parent_ns: Optional[str] = None
        parent_nsmap: Optional[NsMap] = None

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
    def get_field_location(cls, field_info: pd.fields.FieldInfo) -> Location:
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
    def get_entity_info(
            cls,
            model_field: pd.fields.ModelField,
    ) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, str]]]:
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

        if is_xml_model(field_type):
            is_model_field = True
        else:
            is_model_field = False

        field_location = cls.get_field_location(field_info)

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
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)
            element.text = encoded
            return element

        def deserialize(self, element: etree.Element) -> Optional[str]:
            return element.text or None

    class AttributeSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            name, ns, nsmap = self.get_entity_info(model_field)
            ns_attrs = model.__xml_ns_attrs__
            name = name or model_field.alias
            ns = ns or (ctx.parent_ns if ns_attrs else None)
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            self.attr_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap, is_attr=True).uri

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
            name, ns, nsmap = self.get_entity_info(model_field)
            name = name or model_field.alias
            ns = ns or ctx.parent_ns
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)

            sub_element = find_element_or_create(element, self.element_name)
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

    class RootSerializer(Serializer):
        def __init__(self, model: Type['pxml.BaseXmlModel']):
            name = model.__xml_tag__ or model.__name__
            ns = model.__xml_ns__
            nsmap = model.__xml_nsmap__
            is_root = model.__custom_root_type__

            self.model = model
            self.nsmap = nsmap
            self.is_root = is_root
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

            ctx = Serializer.Context(
                parent_ns=ns,
                parent_nsmap=nsmap,
                parent_is_root=is_root,
            )
            self.field_serializers = {
                model_subfield.alias: self.build_field_serializer(model, model_subfield, ctx)
                for field_name, model_subfield in model.__fields__.items()
            }

        def serialize(
                self, element: Optional[etree.Element], value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return None

            if element is None:
                element = create_element(self.element_name, nsmap=self.nsmap)

            for field_name, field_serializer in self.field_serializers.items():
                field_serializer.serialize(element, getattr(value, field_name), encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: etree.Element) -> 'pxml.BaseXmlModel':
            result = {
                field_name: field_value
                for field_name, field_serializer in self.field_serializers.items()
                if (field_value := field_serializer.deserialize(element)) is not None
            }
            if self.is_root:
                obj = result['__root__']
            else:
                obj = result

            return self.model.parse_obj(obj)

    class DeferredSerializer(Serializer):

        def __init__(self, model_field: pd.fields.ModelField):
            assert is_xml_model(model_field.type_), "unexpected model field type"
            self.model: Type[pxml.BaseXmlModel] = model_field.type_

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            assert self.model.__xml_serializer__ is not None, "model is partially initialized"

            return self.model.__xml_serializer__.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

        def deserialize(self, element: etree.Element) -> Optional['pxml.BaseXmlModel']:
            assert self.model.__xml_serializer__ is not None, "model is partially initialized"

            return self.model.__xml_serializer__.deserialize(element)

    class ElementSerializer(DeferredSerializer):

        def __init__(
                self,
                root_model: Type['pxml.BaseXmlModel'],
                model_field: pd.fields.ModelField,
                ctx: Serializer.Context,
        ):
            super().__init__(model_field)
            name, ns, nsmap = self.get_entity_info(model_field)
            field_name = model_field.alias

            model = self.model
            name = name or model.__xml_tag__ or field_name or model.__name__
            ns = ns or model.__xml_ns__
            nsmap = merge_nsmaps(nsmap, model.__xml_nsmap__, root_model.__xml_nsmap__, ctx.parent_nsmap)

            self.nsmap = nsmap
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return None

            sub_element = create_element(self.element_name, nsmap=self.nsmap)
            super().serialize(sub_element, value, encoder=encoder, skip_empty=skip_empty)

            if skip_empty and not sub_element.text and not sub_element.attrib and len(sub_element) == 0:
                return None
            else:
                element.append(sub_element)
                return sub_element

        def deserialize(self, element: etree.Element) -> Optional['pxml.BaseXmlModel']:
            if (sub_element := element.find(self.element_name)) is not None:
                return super().deserialize(sub_element)
            else:
                return None

    @classmethod
    def build_root(cls, model: Type['pxml.BaseXmlModel']) -> 'RootSerializer':
        return cls.RootSerializer(model)

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif not ctx.parent_is_root and field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif ctx.parent_is_root and field_location is Location.MISSING:
            return cls.DeferredSerializer(model_field)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "attributes of model type are not supported",
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
            name, ns, nsmap = self.get_entity_info(model_field)
            name = name or model_field.alias

            self.parent_ns = ns = ns or ctx.parent_ns
            self.parent_nsmap = nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)
            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
            self.ns_attrs = model.__xml_ns_attrs__

    class AttributesSerializer(BaseSerializer):
        def serialize(
                self, element: etree.Element, value: Dict[str, Any], *, encoder: XmlEncoder, skip_empty: bool = False
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
                self, element: etree.Element, value: Dict[str, Any], *, encoder: XmlEncoder, skip_empty: bool = False
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
        assert len(model_field.sub_fields) == 1, "unexpected model field subfields number"

        value_field = model_field.sub_fields[0]
        value_type = value_field.type_

        if PydanticShapeType.from_shape(value_field.shape) is not PydanticShapeType.SCALAR:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "mapping value should be of scalar type",
            )

        if is_xml_model(value_type):
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "mapping value can't be of model type",
            )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.AttributesSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "attributes of mapping type are not supported",
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

            name, ns, nsmap = self.get_entity_info(model_field)
            name = name or model_field.alias
            ns = ns or ctx.parent_ns
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

            item_field = deepcopy(model_field.sub_fields[0])
            item_field.name = model_field.name
            item_field.alias = model_field.alias
            self.serializer = self.build_field_serializer(
                model,
                item_field,
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
        assert model_field.sub_fields is not None, "unexpected model field"
        assert len(model_field.sub_fields) == 1, "unexpected subfields number"

        is_root = model.__custom_root_type__
        item_field = model_field.sub_fields[0]

        if PydanticShapeType.from_shape(item_field.shape) in (
            PydanticShapeType.HOMOGENEOUS,
            PydanticShapeType.HETEROGENEOUS,
        ):
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "collection elements can't be of collection type",
            )

        if is_root and field_location is Location.MISSING:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "root model collections should be marked as elements",
            )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "attributes of collection type are not supported",
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

            name, ns, nsmap = self.get_entity_info(model_field)
            name = name or model_field.alias
            ns = ns or ctx.parent_ns
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            self.element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

            self.serializers = []
            for sub_field in model_field.sub_fields:
                sub_field = deepcopy(sub_field)
                sub_field.name = model_field.name
                sub_field.alias = model_field.alias

                self.serializers.append(
                    self.build_field_serializer(
                        model,
                        sub_field,
                        dc.replace(
                            ctx,
                            parent_is_root=True,
                            parent_ns=ns,
                            parent_nsmap=nsmap,
                        ),
                    ),
                )

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
        assert model_field.sub_fields is not None, "unexpected model field"

        is_root = model.__custom_root_type__

        for item_field in model_field.sub_fields:
            if PydanticShapeType.from_shape(item_field.shape) in (
                PydanticShapeType.HOMOGENEOUS,
                PydanticShapeType.HETEROGENEOUS,
            ):
                raise errors.ModelFieldError(
                    model.__name__, model_field.name, "collection elements can't be of collection type",
                )

            if is_root and field_location is Location.MISSING:
                raise errors.ModelFieldError(
                    model.__name__, model_field.name, "root model collections should be marked as elements",
                )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "attributes of collection type are not supported",
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
            path, ns, nsmap = self.get_entity_info(model_field)
            ns = ns or ctx.parent_ns
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            model_field = deepcopy(model_field)
            field_info = model_field.field_info

            assert path is not None, "path is not provided"
            assert isinstance(field_info, pxml.XmlWrapperInfo), "unexpected field info type"

            # copy field_info from wrapped entity
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
