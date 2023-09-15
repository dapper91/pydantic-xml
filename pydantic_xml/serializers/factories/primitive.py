from typing import Any, Dict, Optional, Union

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import SearchMode, Serializer
from pydantic_xml.typedefs import EntityLocation, NsMap
from pydantic_xml.utils import QName, merge_nsmaps

PrimitiveTypeSchema = Union[
    pcs.NoneSchema,
    pcs.BoolSchema,
    pcs.IntSchema,
    pcs.FloatSchema,
    pcs.StringSchema,
    pcs.BytesSchema,
    pcs.DateSchema,
    pcs.TimeSchema,
    pcs.DatetimeSchema,
    pcs.TimedeltaSchema,
    pcs.UrlSchema,
    pcs.MultiHostUrlSchema,
    pcs.JsonSchema,
    pcs.LiteralSchema,
    pcs.LaxOrStrictSchema,
    pcs.IsInstanceSchema,
]


class TextSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: PrimitiveTypeSchema, ctx: Serializer.Context) -> 'TextSerializer':
        computed = ctx.field_computed

        return cls(computed)

    def __init__(self, computed: bool):
        self._computed = computed

    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None and skip_empty:
            return element

        element.set_text(str(encoded))
        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        if self._computed:
            return None

        if element is None:
            return None

        return element.pop_text() or None


class AttributeSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: PrimitiveTypeSchema, ctx: Serializer.Context) -> 'AttributeSerializer':
        namespaced_attrs = ctx.namespaced_attrs
        name = ctx.entity_path or ctx.field_alias or ctx.field_name
        ns = ctx.entity_ns or (ctx.parent_ns if namespaced_attrs else None)
        nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
        computed = ctx.field_computed

        if name is None:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

        return cls(name, ns, nsmap, computed)

    def __init__(self, name: str, ns: Optional[str], nsmap: Optional[NsMap], computed: bool):
        self._attr_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap, is_attr=True).uri
        self._computed = computed

    @property
    def attr_name(self) -> str:
        return self._attr_name

    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None and skip_empty:
            return element

        element.set_attribute(self._attr_name, str(encoded))

        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        if self._computed:
            return None

        if element is None:
            return None

        return element.pop_attrib(self._attr_name)


class ElementSerializer(TextSerializer):
    @classmethod
    def from_core_schema(cls, schema: PrimitiveTypeSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        name = ctx.entity_path or ctx.field_alias or ctx.field_name
        ns = ctx.entity_ns or ctx.parent_ns
        nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
        search_mode = ctx.search_mode
        computed = ctx.field_computed

        if name is None:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

        return cls(name, ns, nsmap, search_mode, computed)

    def __init__(self, name: str, ns: Optional[str], nsmap: Optional[NsMap], search_mode: SearchMode, computed: bool):
        super().__init__(computed)

        self._nsmap = nsmap
        self._search_mode = search_mode
        self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None and skip_empty:
            return element

        sub_element = element.make_element(self._element_name, nsmap=self._nsmap)
        super().serialize(sub_element, value, encoded, skip_empty=skip_empty)
        if skip_empty and sub_element.is_empty():
            return None
        else:
            element.append_element(sub_element)
            return sub_element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        if self._computed:
            return None

        if element is not None and \
                (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
            return super().deserialize(sub_element, context=context)
        else:
            return None


def from_core_schema(schema: PrimitiveTypeSchema, ctx: Serializer.Context) -> Serializer:
    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        return AttributeSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is None:
        return TextSerializer.from_core_schema(schema, ctx)
    else:
        raise AssertionError("unreachable")
