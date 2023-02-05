from typing import Any, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Location, Serializer
from pydantic_xml.utils import QName, merge_nsmaps


class PrimitiveTypeSerializerFactory:
    """
    Primitive type serializer factory.
    """

    class TextSerializer(Serializer):
        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)
            element.set_text(encoded)
            return element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[str]:
            if element is None:
                return None

            return element.pop_text() or None

    class AttributeSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            name, ns, nsmap = self._get_entity_info(model_field)
            ns_attrs = model.__xml_ns_attrs__
            name = name or model_field.alias
            ns = ns or (ctx.parent_ns if ns_attrs else None)
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            self._attr_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap, is_attr=True).uri

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None and skip_empty:
                return element

            encoded = encoder.encode(value)
            element.set_attribute(self._attr_name, encoded)

            return element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[str]:
            if element is None:
                return None

            return element.pop_attrib(self._attr_name)

    class ElementSerializer(TextSerializer):
        def __init__(self, model_field: pd.fields.ModelField, ctx: Serializer.Context):
            name, ns, nsmap = self._get_entity_info(model_field)
            name = name or model_field.alias
            ns = ns or ctx.parent_ns
            self._search_mode = ctx.search_mode
            self._nsmap = nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)
            self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None and skip_empty:
                return element

            sub_element = element.make_element(self._element_name, nsmap=self._nsmap)
            super().serialize(sub_element, value, encoder=encoder, skip_empty=skip_empty)
            if skip_empty and sub_element.is_empty():
                return None
            else:
                element.append_element(sub_element)
                return sub_element

        def deserialize(self, element: Optional[XmlElementReader]) -> Any:
            if element is not None and \
                    (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
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
        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            return cls.AttributeSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.TextSerializer()
        else:
            raise AssertionError("unreachable")
