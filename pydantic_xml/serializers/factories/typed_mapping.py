from typing import List

from pydantic_core import core_schema as pcs

from pydantic_xml import errors
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import EntityLocation

from .mapping import AttributesSerializer, ElementSerializer


def from_core_schema(schema: pcs.TypedDictSchema, ctx: Serializer.Context) -> Serializer:
    values_schemas: List[pcs.CoreSchema] = []
    for field_name, field in schema['fields'].items():
        values_schemas.append(field['schema'])

    for computed_field in schema['computed_fields']:
        values_schemas.append(computed_field['return_schema'])

    for val_schema in values_schemas:
        val_schema, val_ctx = Serializer.preprocess_schema(val_schema, ctx)
        if TYPE_FAMILY.get(val_schema['type']) is not SchemaTypeFamily.PRIMITIVE:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "mapping values must be of a primitive type")

    if ctx.entity_location is EntityLocation.ELEMENT:
        return ElementSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is None:
        return AttributesSerializer.from_core_schema(schema, ctx)
    elif ctx.entity_location is EntityLocation.ATTRIBUTE:
        raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of mapping type are not supported")
    else:
        raise AssertionError("unreachable")
