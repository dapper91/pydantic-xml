from typing import Any, Dict, Optional, Sized

from pydantic_core import core_schema as pcs

from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import SearchMode, Serializer
from pydantic_xml.typedefs import Location, NsMap
from pydantic_xml.utils import QName, merge_nsmaps, select_ns


class ElementPathSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.CoreSchema, ctx: Serializer.Context) -> 'ElementPathSerializer':
        path = ctx.entity_path
        ns = select_ns(ctx.entity_ns, ctx.parent_ns)
        nsmap = merge_nsmaps(ctx.entity_nsmap, ctx.parent_nsmap)
        search_mode = ctx.search_mode
        computed = ctx.field_computed

        assert path is not None, "path is not provided"

        ctx = ctx.child(entity_info=ctx.entity_wrapped)
        inner_serializer = Serializer.parse_core_schema(schema, ctx)

        return cls(path, ns, nsmap, search_mode, computed, inner_serializer)

    def __init__(
            self,
            path: str,
            ns: Optional[str],
            nsmap: Optional[NsMap],
            search_mode: SearchMode,
            computed: bool,
            inner_serializer: Serializer,
    ):
        self._path = tuple(QName.from_alias(tag=part, ns=ns, nsmap=nsmap).uri for part in path.split('/'))
        self._nsmap = nsmap
        self._search_mode = search_mode
        self._computed = computed
        self._inner_serializer = inner_serializer

    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return element

        if skip_empty and isinstance(value, Sized) and len(value) == 0:
            return element

        for part in self._path:
            element = element.find_element_or_create(part, self._search_mode, nsmap=self._nsmap)

        self._inner_serializer.serialize(element, value, encoded, skip_empty=skip_empty)

        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[Any]:
        if self._computed:
            return None

        if element is None:
            return None

        if sub_elements := element.find_sub_element(self._path, self._search_mode):
            sub_element = sub_elements[-1]
            if len(sub_elements) == len(self._path):
                sourcemap[loc] = sub_element.get_sourceline()
                return self._inner_serializer.deserialize(sub_element, context=context, sourcemap=sourcemap, loc=loc)
            else:
                return None
        else:
            return None


def from_core_schema(schema: pcs.CoreSchema, ctx: Serializer.Context) -> Serializer:
    return ElementPathSerializer.from_core_schema(schema, ctx)
