from typing import Any, Dict, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Location, PydanticShapeType, Serializer, is_xml_model
from pydantic_xml.utils import QName, merge_nsmaps


class MappingSerializerFactory:
    """
    Mapping type serializer factory.
    """

    class AttributesSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            name, ns, nsmap = self._get_entity_info(model_field)
            self._ns = ns or ctx.parent_ns
            self._nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)
            self._ns_attrs = model.__xml_ns_attrs__

        def serialize(
                self, element: XmlElementWriter, value: Dict[str, Any], *, encoder: XmlEncoder, skip_empty: bool = False
        ) -> Optional[XmlElementWriter]:
            if value is None:
                return element

            ns = self._nsmap.get(self._ns) if self._ns_attrs and self._ns else None
            element.set_attributes({
                QName(tag=attr, ns=ns).uri: encoder.encode(val)
                for attr, val in value.items()
            })

            return element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[Dict[str, str]]:
            if element is None:
                return None

            if (attributes := element.pop_attributes()) is None:
                return None

            return {
                QName.from_uri(attr).tag if self._ns_attrs else attr: val
                for attr, val in attributes.items()
            }

    class ElementSerializer(AttributesSerializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            super().__init__(model, model_field, ctx)

            name, ns, nsmap = self._get_entity_info(model_field)
            self._name = name or model_field.alias
            self._element_name = QName.from_alias(tag=self._name, ns=self._ns, nsmap=self._nsmap).uri
            self._search_mode = ctx.search_mode

        def serialize(
                self, element: XmlElementWriter, value: Dict[str, Any], *, encoder: XmlEncoder, skip_empty: bool = False
        ) -> Optional[XmlElementWriter]:
            if skip_empty and len(value) == 0:
                return element

            sub_element = element.make_element(self._element_name, nsmap=self._nsmap)
            super().serialize(sub_element, value, encoder=encoder, skip_empty=skip_empty)
            if skip_empty and sub_element.is_empty():
                return None
            else:
                element.append_element(sub_element)
                return sub_element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[Dict[str, str]]:
            if element and (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
                return super().deserialize(sub_element)
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
