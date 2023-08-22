from typing import Any, Dict, List, Optional, Union

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import EntityLocation

HomogeneousCollectionTypeSchema = Union[
    pcs.TupleVariableSchema,
    pcs.ListSchema,
    pcs.SetSchema,
    pcs.FrozenSetSchema,
]


class ElementSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: HomogeneousCollectionTypeSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        computed = ctx.field_computed
        inner_serializer = Serializer.parse_core_schema(schema['items_schema'], ctx)

        return cls(computed, inner_serializer)

    def __init__(self, computed: bool, inner_serializer: Serializer):
        self._computed = computed
        self._inner_serializer = inner_serializer

    def serialize(
            self, element: XmlElementWriter, value: List[Any], encoded: List[Any], *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return element

        if skip_empty and len(value) == 0:
            return element

        for val, enc in zip(value, encoded):
            if skip_empty and val is None:
                continue

            self._inner_serializer.serialize(element, val, enc, skip_empty=skip_empty)

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

        result = []
        while (value := self._inner_serializer.deserialize(element, context=context)) is not None:
            result.append(value)

        return result or None


def from_core_schema(schema: HomogeneousCollectionTypeSchema, ctx: Serializer.Context) -> Serializer:
    items_schema = schema['items_schema']
    items_schema, ctx = Serializer.preprocess_schema(items_schema, ctx)

    items_type_family = TYPE_FAMILY.get(items_schema['type'])
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
