from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.serializers.serializer import Serializer


def from_core_schema(schema: pcs.CallSchema, ctx: Serializer.Context) -> Serializer:
    raise errors.ModelError("type call is not supported")
