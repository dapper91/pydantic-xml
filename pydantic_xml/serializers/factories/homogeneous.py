import itertools as it
from typing import Any, Dict, List, Optional, Union

import pydantic as pd
from pydantic_core import core_schema as pcs

from pydantic_xml import errors, utils
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import EntityLocation, Location

HomogeneousCollectionTypeSchema = Union[
    pcs.TupleSchema,
    pcs.ListSchema,
    pcs.SetSchema,
    pcs.FrozenSetSchema,
]


class ElementSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: HomogeneousCollectionTypeSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        model_name = ctx.model_name
        computed = ctx.field_computed

        items_schema = schema['items_schema']
        if isinstance(items_schema, list):
            assert len(items_schema) == 1, "unexpected items schema type"
            items_schema = items_schema[0]

        inner_serializer = Serializer.parse_core_schema(items_schema, ctx)

        return cls(model_name, computed, inner_serializer)

    def __init__(self, model_name: str, computed: bool, inner_serializer: Serializer):
        self._model_name = model_name
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
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[List[Any]]:
        if self._computed:
            return None

        if element is None:
            return None

        serializer = self._inner_serializer
        result: List[Any] = []
        item_errors: Dict[Union[None, str, int], pd.ValidationError] = {}
        for idx in it.count():
            try:
                value = serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc + (idx,))
                if value is None:
                    break
            except pd.ValidationError as err:
                item_errors[idx] = err
            else:
                result.append(value)

        if item_errors:
            raise utils.build_validation_error(title=self._model_name, errors_map=item_errors)

        return result or None


def from_core_schema(schema: HomogeneousCollectionTypeSchema, ctx: Serializer.Context) -> Serializer:
    items_schema = schema['items_schema']
    if isinstance(items_schema, list):
        assert len(items_schema) == 1, "unexpected items schema type"
        items_schema = items_schema[0]

    items_schema, ctx = Serializer.preprocess_schema(items_schema, ctx)

    items_type_family = TYPE_FAMILY.get(items_schema['type'])
    if items_type_family not in (
        SchemaTypeFamily.PRIMITIVE,
        SchemaTypeFamily.MODEL,
        SchemaTypeFamily.MAPPING,
        SchemaTypeFamily.TYPED_MAPPING,
        SchemaTypeFamily.UNION,
        SchemaTypeFamily.IS_INSTANCE,
        SchemaTypeFamily.TUPLE,
    ):
        raise errors.ModelFieldError(
            ctx.model_name, ctx.field_name, "collection item must be of primitive, model, mapping, union or tuple type",
        )

    if items_type_family not in (
            SchemaTypeFamily.MODEL,
            SchemaTypeFamily.UNION,
            SchemaTypeFamily.TUPLE,
    ) and ctx.entity_location is None:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is None:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of collection types are not supported")
    else:
        raise AssertionError("unreachable")
