from pydantic_core import core_schema as pcs

from pydantic_xml.element import native
from pydantic_xml.serializers.serializer import Serializer

from . import primitive, raw


def from_core_schema(schema: pcs.IsInstanceSchema, ctx: Serializer.Context) -> Serializer:
    field_cls = schema['cls']

    if issubclass(field_cls, native.ElementT):
        return raw.from_core_schema(schema, ctx)
    else:
        return primitive.from_core_schema(schema, ctx)
