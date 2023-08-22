from typing import Any, Dict, List, Optional, Tuple

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import EntityLocation


class ElementSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.TuplePositionalSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        computed = ctx.field_computed
        inner_serializers: List[Serializer] = []
        for item_schema in schema['items_schema']:
            inner_serializers.append(Serializer.parse_core_schema(item_schema, ctx))

        return cls(computed, tuple(inner_serializers))

    def __init__(self, computed: bool, inner_serializers: Tuple[Serializer, ...]):
        self._computed = computed
        self._inner_serializers = inner_serializers

    def serialize(
            self, element: XmlElementWriter, value: List[Any], encoded: List[Any], *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return element

        if skip_empty and len(value) == 0:
            return element

        if len(value) != len(self._inner_serializers):
            raise errors.SerializationError("value length is incorrect")

        for serializer, val, enc in zip(self._inner_serializers, value, encoded):
            serializer.serialize(element, val, enc, skip_empty=skip_empty)

        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
    ) -> Optional[List[Any]]:
        if self._computed:
            return None

        if element is None:
            return None

        return [
            serializer.deserialize(element, context=context)
            for serializer in self._inner_serializers
        ]


def from_core_schema(schema: pcs.TuplePositionalSchema, ctx: Serializer.Context) -> Serializer:
    for item_schema in schema['items_schema']:
        item_schema, ctx = Serializer.preprocess_schema(item_schema, ctx)

        items_type_family = TYPE_FAMILY.get(item_schema['type'])
        if items_type_family not in (
                SchemaTypeFamily.PRIMITIVE,
                SchemaTypeFamily.MODEL,
                SchemaTypeFamily.MAPPING,
                SchemaTypeFamily.TYPED_MAPPING,
                SchemaTypeFamily.UNION,
                SchemaTypeFamily.IS_INSTANCE,
        ):
            raise errors.ModelFieldError(
                ctx.model_name, ctx.field_name, "collection item must be of primitive, model, mapping or union type",
            )

        if items_type_family not in (SchemaTypeFamily.MODEL, SchemaTypeFamily.UNION) and ctx.entity_location is None:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is None:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of collection types are not supported")
    else:
        raise AssertionError("unreachable")
