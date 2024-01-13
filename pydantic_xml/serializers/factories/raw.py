from typing import Any, Dict, Optional

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import SearchMode, Serializer
from pydantic_xml.typedefs import EntityLocation, Location, NsMap
from pydantic_xml.utils import QName, merge_nsmaps, select_ns


class ElementSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.IsInstanceSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        name = ctx.entity_path or ctx.field_alias or ctx.field_name
        ns = select_ns(ctx.entity_ns, ctx.parent_ns)
        nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
        search_mode = ctx.search_mode
        computed = ctx.field_computed

        if name is None:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

        return cls(name, ns, nsmap, search_mode, computed)

    def __init__(self, name: str, ns: Optional[str], nsmap: Optional[NsMap], search_mode: SearchMode, computed: bool):
        self._computed = computed
        self._nsmap = nsmap
        self._search_mode = search_mode
        self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return element

        sub_element = element.from_native(value)
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
    ) -> Optional[str]:
        if self._computed:
            return None

        if element is None:
            return None

        if (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
            sourcemap[loc] = sub_element.get_sourceline()
            return sub_element.to_native()
        else:
            return None


def from_core_schema(schema: pcs.IsInstanceSchema, ctx: Serializer.Context) -> Serializer:
    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is None:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of raw types are not supported")
    else:
        raise AssertionError("unreachable")
