import typing
from typing import Any, Dict, Optional

from pydantic_core import core_schema as pcs

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers import factories
from pydantic_xml.serializers.factories.model import ModelProxySerializer
from pydantic_xml.serializers.factories.primitive import AttributeSerializer
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, SearchMode, Serializer
from pydantic_xml.typedefs import Location


class ModelSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.TaggedUnionSchema, ctx: Serializer.Context) -> 'ModelSerializer':
        computed = ctx.field_computed
        search_mode = ctx.search_mode

        discriminator = schema['discriminator']
        if not isinstance(discriminator, str):
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "only string discriminators are supported")

        discriminating_attr_name: Optional[str] = None
        inner_serializers: Dict[str, ModelProxySerializer] = {}
        for tag, choice_schema in schema['choices'].items():
            if not isinstance(tag, str):
                raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "tagged union only supports string tags")

            serializer = Serializer.parse_core_schema(choice_schema, ctx)
            assert isinstance(serializer, ModelProxySerializer), "unexpected serializer type"
            inner_serializers[tag] = serializer

            model_serializer = serializer.model_serializer
            assert isinstance(model_serializer, factories.model.ModelSerializer), "unexpected model serializer type"

            discriminator_serializer = model_serializer.fields_serializers.get(discriminator)
            if not isinstance(discriminator_serializer, AttributeSerializer):
                raise errors.ModelFieldError(
                    ctx.model_name, ctx.field_name, "discriminator field must be an xml attribute",
                )

            if discriminating_attr_name is not None and discriminating_attr_name != discriminator_serializer.attr_name:
                raise errors.ModelFieldError(
                    ctx.model_name, ctx.field_name, "sub-models discriminating attributes must have the same name",
                )
            discriminating_attr_name = discriminator_serializer.attr_name

        assert discriminating_attr_name is not None, "schema choices are not provided"

        return cls(computed, discriminator, discriminating_attr_name, inner_serializers, search_mode)

    def __init__(
            self,
            computed: bool,
            discriminator: str,
            discriminating_attr_name: str,
            inner_serializers: Dict[str, ModelProxySerializer],
            search_mode: SearchMode,
    ):
        self._computed = computed
        self._discriminator = discriminator
        self._discriminating_attr_name = discriminating_attr_name
        self._inner_serializers = inner_serializers
        self._search_mode = search_mode

    def serialize(
            self,
            element: XmlElementWriter,
            value: 'pxml.BaseXmlModel',
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if (tag := encoded.get(self._discriminator)) and (serializer := self._inner_serializers[tag]):
            return serializer.serialize(element, value, encoded, skip_empty=skip_empty)

        return None

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional['pxml.BaseXmlModel']:
        if self._computed:
            return None

        if element is None:
            return None

        for tag, serializer in self._inner_serializers.items():
            sub_element = element.find_element(
                serializer.element_name,
                self._search_mode,
                look_behind=False,
                step_forward=False,
            )
            if sub_element is not None and sub_element.get_attrib(self._discriminating_attr_name) == tag:
                sourcemap[loc] = sub_element.get_sourceline()
                return serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc)

        return None


def from_core_schema(schema: pcs.TaggedUnionSchema, ctx: Serializer.Context) -> Serializer:
    for tag, choice_schema in schema['choices'].items():
        choice_schema, ctx = Serializer.preprocess_schema(choice_schema, ctx)
        choice_type_family = TYPE_FAMILY.get(choice_schema['type'])

        if choice_type_family is not SchemaTypeFamily.MODEL:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "tagged union must be of a model type")

        choice_schema = typing.cast(pcs.ModelSchema, choice_schema)
        if choice_schema['root_model']:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "tagged union doesn't support root models")

    return ModelSerializer.from_core_schema(schema, ctx)
