from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.serializers.serializer import Serializer

from . import heterogeneous, homogeneous


def from_core_schema(schema: pcs.TupleSchema, ctx: Serializer.Context) -> Serializer:
    # Starting from pydantic-core 2.15.0 `tuple-positional` and `tuple-variable` types
    # had been merged into a single `tuple` type to be able to handle variadic tuples (PEP-646).
    # Since that point is not possible to separate tuple into homogeneous and heterogeneous collections
    # by its type but only by presence of the `variadic_item_index` field in the schema.
    if (variadic_item_index := schema.get('variadic_item_index')) is not None:
        if variadic_item_index != 0:
            raise errors.ModelFieldError(
                ctx.model_name, ctx.field_name, "variadic tuples with prefixed items are not supported",
            )
        return homogeneous.from_core_schema(schema, ctx)
    else:
        return heterogeneous.from_core_schema(schema, ctx)
