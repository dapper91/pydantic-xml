import inspect

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.serializers.factories import named_tuple
from pydantic_xml.serializers.serializer import Serializer


def from_core_schema(schema: pcs.CallSchema, ctx: Serializer.Context) -> Serializer:
    func = schema['function']

    if inspect.isclass(func) and issubclass(func, tuple):
        return named_tuple.from_core_schema(schema, ctx)
    else:
        raise errors.ModelError("type call is not supported")
