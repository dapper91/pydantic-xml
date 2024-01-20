from typing import Any, Dict, List, Optional, Set, Tuple

import pydantic as pd
from pydantic_core import core_schema as pcs

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.factories.model import ModelProxySerializer
from pydantic_xml.serializers.serializer import TYPE_FAMILY, SchemaTypeFamily, Serializer
from pydantic_xml.typedefs import Location


class PrimitiveTypeSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.UnionSchema, ctx: Serializer.Context) -> 'PrimitiveTypeSerializer':
        computed = ctx.field_computed
        inner_serializers: List[Serializer] = []
        for choice_schema in schema['choices']:
            if isinstance(choice_schema, tuple):
                choice_schema, label = choice_schema

            inner_serializers.append(Serializer.parse_core_schema(choice_schema, ctx))

        assert len(inner_serializers) > 0, "union choice is not provided"

        # all union types serializers must be of the same type
        if len(set(type(s) for s in inner_serializers)) > 1:
            raise TypeError("unions of different primitive types are not supported")

        return cls(computed, inner_serializers[0])

    def __init__(self, computed: bool, inner_serializer: Serializer):
        self._computed = computed
        self._inner_serializer = inner_serializer

    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        return self._inner_serializer.serialize(element, value, encoded, skip_empty=skip_empty)

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[str]:
        if self._computed:
            return None

        return self._inner_serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc)


class ModelSerializer(Serializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.UnionSchema, ctx: Serializer.Context) -> 'ModelSerializer':
        computed = ctx.field_computed
        inner_serializers: List[ModelProxySerializer] = []
        for choice_schema in schema['choices']:
            if isinstance(choice_schema, tuple):
                choice_schema, label = choice_schema

            serializer = Serializer.parse_core_schema(choice_schema, ctx)
            assert isinstance(serializer, ModelProxySerializer), "unexpected serializer type"

            inner_serializers.append(serializer)

        assert len(inner_serializers) > 0, "union choice is not provided"

        return cls(computed, tuple(inner_serializers))

    def __init__(self, computed: bool, inner_serializers: Tuple[ModelProxySerializer, ...]):
        self._computed = computed
        self._inner_serializers = inner_serializers

    def serialize(
            self,
            element: XmlElementWriter,
            value: 'pxml.BaseXmlModel',
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        for serializer in self._inner_serializers:
            if serializer.model is type(value):
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

        last_error: Optional[Exception] = None
        result: Any = None
        for serializer in self._inner_serializers:
            snapshot = element.create_snapshot()
            try:
                if (result := serializer.deserialize(snapshot, context=context, sourcemap=sourcemap, loc=loc)) is None:
                    continue
                else:
                    element.apply_snapshot(snapshot)
                    return result
            except pd.ValidationError as e:
                last_error = e

        if last_error is not None:
            element.step_forward()
            raise last_error

        return result


def from_core_schema(schema: pcs.UnionSchema, ctx: Serializer.Context) -> Serializer:
    choice_families: Set[SchemaTypeFamily] = set()
    for choice_schema in schema['choices']:
        if isinstance(choice_schema, tuple):
            choice_schema, label = choice_schema

        choice_schema, ctx = Serializer.preprocess_schema(choice_schema, ctx)
        choice_type_family = TYPE_FAMILY.get(choice_schema['type'])

        if choice_type_family not in (SchemaTypeFamily.PRIMITIVE, SchemaTypeFamily.IS_INSTANCE, SchemaTypeFamily.MODEL):
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "union must be of primitive or model type")

        choice_families.add(choice_type_family)

    assert len(choice_families) > 0, "union choices are not provided"

    if (SchemaTypeFamily.PRIMITIVE in choice_families or SchemaTypeFamily.IS_INSTANCE in choice_families) and \
            SchemaTypeFamily.MODEL in choice_families:
        raise TypeError("unions of combined primitive and model types are not supported")

    choice_family = choice_families.pop()
    if choice_family is SchemaTypeFamily.MODEL:
        return ModelSerializer.from_core_schema(schema, ctx)
    elif choice_family is SchemaTypeFamily.PRIMITIVE:
        return PrimitiveTypeSerializer.from_core_schema(schema, ctx)
    else:
        raise AssertionError("unreachable")
