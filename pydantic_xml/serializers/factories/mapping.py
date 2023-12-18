from typing import Any, Dict, Optional

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, SearchMode, Serializer
from pydantic_xml.typedefs import EntityLocation, Location, NsMap
from pydantic_xml.utils import QName, merge_nsmaps, select_ns


class AttributesSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.CoreSchema, ctx: Serializer.Context) -> 'AttributesSerializer':
        ns = select_ns(ctx.entity_ns, ctx.parent_ns)
        nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
        namespaced_attrs = ctx.namespaced_attrs
        computed = ctx.field_computed

        return cls(ns, nsmap, namespaced_attrs, computed)

    def __init__(self, ns: Optional[str], nsmap: Optional[NsMap], namespaced_attrs: bool, computed: bool):
        self._ns = ns
        self._namespaced_attrs = namespaced_attrs
        self._nsmap = nsmap
        self._computed = computed

    def serialize(
            self,
            element: XmlElementWriter,
            value: Dict[str, Any],
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return element

        ns = self._nsmap.get(self._ns) if self._namespaced_attrs and self._ns and self._nsmap else None
        element.set_attributes({
            QName(tag=attr, ns=ns).uri: str(enc)
            for attr, enc in encoded.items()
        })

        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[Dict[str, str]]:
        if self._computed:
            return None

        if element is None or (attributes := element.pop_attributes()) is None:
            return None

        return {
            QName.from_uri(attr).tag if self._namespaced_attrs else attr: val
            for attr, val in attributes.items()
        }


class ElementSerializer(AttributesSerializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.CoreSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        name = ctx.entity_path or ctx.field_alias or ctx.field_name
        ns = select_ns(ctx.entity_ns, ctx.parent_ns)
        nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
        namespaced_attrs = ctx.namespaced_attrs
        search_mode = ctx.search_mode
        computed = ctx.field_computed

        if name is None:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

        return cls(name, ns, nsmap, namespaced_attrs, search_mode, computed)

    def __init__(
            self,
            name: str,
            ns: Optional[str],
            nsmap: Optional[NsMap],
            namespaced_attrs: bool,
            search_mode: SearchMode,
            computed: bool,
    ):
        super().__init__(ns, nsmap, namespaced_attrs, computed)
        self._search_mode = search_mode
        self._name = name
        self._element_name = QName.from_alias(tag=self._name, ns=self._ns, nsmap=self._nsmap).uri

    def serialize(
            self,
            element: XmlElementWriter,
            value: Dict[str, Any],
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if skip_empty and len(value) == 0:
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
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[Dict[str, str]]:
        if self._computed:
            return None

        if element and (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
            sourcemap[loc] = sub_element.get_sourceline()
            return super().deserialize(sub_element, context=context, sourcemap=sourcemap, loc=loc)
        else:
            return None


def from_core_schema(schema: pcs.DictSchema, ctx: Serializer.Context) -> Serializer:
    key_schema = schema['keys_schema']
    key_schema, key_ctx = Serializer.preprocess_schema(key_schema, ctx)

    val_schema = schema['values_schema']
    val_schema, val_ctx = Serializer.preprocess_schema(val_schema, ctx)

    if TYPE_FAMILY.get(key_schema['type']) is not SchemaTypeFamily.PRIMITIVE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "mapping key must be of a primitive type")
    if TYPE_FAMILY.get(val_schema['type']) is not SchemaTypeFamily.PRIMITIVE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "mapping value must be of a primitive type")

    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is None:
        return AttributesSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of mapping type are not supported")
    else:
        raise AssertionError("unreachable")
