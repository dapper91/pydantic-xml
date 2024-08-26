import typing
from typing import Any, Dict, List, Optional, Tuple

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.factories import heterogeneous
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import EntityLocation, Location


class ElementSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.ArgumentsSchema, ctx: Serializer.Context) -> 'ElementSerializer':
        model_name = ctx.model_name
        computed = ctx.field_computed
        inner_serializers: List[Serializer] = []
        for argument_schema in schema['arguments_schema']:
            param_schema = argument_schema['schema']
            inner_serializers.append(Serializer.parse_core_schema(param_schema, ctx))

        return cls(model_name, computed, tuple(inner_serializers))

    def __init__(self, model_name: str, computed: bool, inner_serializers: Tuple[Serializer, ...]):
        self._inner_serializer = heterogeneous.ElementSerializer(model_name, computed, inner_serializers)

    def serialize(
            self,
            element: XmlElementWriter,
            value: List[Any],
            encoded: List[Any],
            *,
            skip_empty: bool = False,
            exclude_none: bool = False,
            exclude_unset: bool = False,
    ) -> Optional[XmlElementWriter]:
        return self._inner_serializer.serialize(
            element, value, encoded, skip_empty=skip_empty, exclude_none=exclude_none, exclude_unset=exclude_unset,
        )

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[List[Any]]:
        return self._inner_serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc)


def from_core_schema(schema: pcs.CallSchema, ctx: Serializer.Context) -> Serializer:
    arguments_schema = typing.cast(pcs.ArgumentsSchema, schema['arguments_schema'])
    for argument_schema in arguments_schema['arguments_schema']:
        param_schema = argument_schema['schema']
        param_schema, ctx = Serializer.preprocess_schema(param_schema, ctx)

        param_type_family = TYPE_FAMILY.get(param_schema['type'])
        if param_type_family not in (
                SchemaTypeFamily.PRIMITIVE,
                SchemaTypeFamily.MODEL,
                SchemaTypeFamily.MAPPING,
                SchemaTypeFamily.TYPED_MAPPING,
                SchemaTypeFamily.UNION,
                SchemaTypeFamily.TAGGED_UNION,
                SchemaTypeFamily.IS_INSTANCE,
                SchemaTypeFamily.CALL,
        ):
            raise errors.ModelFieldError(
                ctx.model_name, ctx.field_name, "tuple item must be of primitive, model, mapping or union type",
            )

        if param_type_family not in (SchemaTypeFamily.MODEL, SchemaTypeFamily.UNION) and ctx.entity_location is None:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "entity name is not provided")

    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(arguments_schema, ctx)
    elif ctx.entity_location is None:
        return ElementSerializer.from_core_schema(arguments_schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of tuple types are not supported")
    else:
        raise AssertionError("unreachable")
