from typing import Any, Dict, List, Optional, Tuple, Union

import pydantic as pd
from pydantic_core import core_schema as pcs

from pydantic_xml import errors, utils
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import EntityLocation, Location


class ElementSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.TupleSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        model_name = ctx.model_name
        computed = ctx.field_computed
        inner_serializers: List[Serializer] = []
        for item_schema in schema['items_schema']:
            inner_serializers.append(Serializer.parse_core_schema(item_schema, ctx))

        return cls(model_name, computed, tuple(inner_serializers))

    def __init__(self, model_name: str, computed: bool, inner_serializers: Tuple[Serializer, ...]):
        self._model_name = model_name
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
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[List[Any]]:
        if self._computed:
            return None

        if element is None:
            return None

        result: List[Any] = []
        item_errors: Dict[Union[None, str, int], pd.ValidationError] = {}
        for idx, serializer in enumerate(self._inner_serializers):
            try:
                result.append(serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc + (idx,)))
            except pd.ValidationError as err:
                item_errors[idx] = err

        if item_errors:
            raise utils.build_validation_error(title=self._model_name, errors_map=item_errors)

        if all((value is None for value in result)):
            return None
        else:
            return result


def from_core_schema(schema: pcs.TupleSchema, ctx: Serializer.Context) -> Serializer:
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
