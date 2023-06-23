import dataclasses as dc
import typing
from typing import Any, List, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.factories.model import ModelSerializerFactory
from pydantic_xml.serializers.serializer import Location, PydanticShapeType, Serializer, SubFieldWrapper, is_xml_model


class UnionSerializerFactory:
    """
    Union type serializer factory.
    """

    class PrimitiveTypeSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            assert model_field.sub_fields is not None, "unexpected model field subfields type"
            assert len(model_field.sub_fields) > 1, "unexpected model field subfields number"

            inner_serializers: List[Serializer] = []
            for sub_field in model_field.sub_fields:
                sub_field = typing.cast(
                    pd.fields.ModelField,
                    SubFieldWrapper(
                        model_field.name,
                        model_field.alias,
                        model_field.field_info,
                        sub_field,
                    ),
                )

                inner_serializers.append(self._build_field_serializer(model, sub_field, ctx))

            # all union types serializers must be of the same type
            if len(set(type(s) for s in inner_serializers)) > 1:
                raise TypeError("unions of different primitive types are not supported")

            self._inner_serializer = inner_serializers[0]

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            return self._inner_serializer.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[str]:
            return self._inner_serializer.deserialize(element)

    class ModelSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            assert model_field.sub_fields is not None, "unexpected model field subfields type"
            assert len(model_field.sub_fields) > 1, "unexpected model field subfields number"

            inner_serializers: List[ModelSerializerFactory.ModelSerializer] = []
            for sub_field in model_field.sub_fields:
                sub_field = typing.cast(
                    pd.fields.ModelField,
                    SubFieldWrapper(
                        model_field.name,
                        model_field.alias,
                        model_field.field_info,
                        sub_field,
                    ),
                )

                serializer = self._build_field_serializer(
                    model,
                    sub_field,
                    dc.replace(ctx, parent_is_root=False),
                )
                assert isinstance(serializer, ModelSerializerFactory.ModelSerializer), "unexpected serializer type"

                inner_serializers.append(serializer)

            self._inner_serializers = inner_serializers

        def serialize(
                self,
                element: XmlElementWriter,
                value: 'pxml.BaseXmlModel',
                *,
                encoder: XmlEncoder,
                skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            for serializer in self._inner_serializers:
                if serializer.model is type(value):
                    return serializer.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

            raise AssertionError("unexpected serialized type")

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[List[Any]]:
            if element is None:
                return None

            last_error: Optional[Exception] = None
            result: Any = None
            for serializer in self._inner_serializers:
                snapshot = element.create_snapshot()
                try:
                    if (result := serializer.deserialize(snapshot)) is None:
                        continue
                    else:
                        element.apply_snapshot(snapshot)
                        return result
                except pd.ValidationError as e:
                    last_error = e

            if last_error is not None:
                raise last_error

            return result

        def resolve_forward_refs(self) -> 'Serializer':
            self._inner_serializers = [
                typing.cast(ModelSerializerFactory.ModelSerializer, serializer.resolve_forward_refs())
                for serializer in self._inner_serializers
            ]

            return self

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        assert model_field.sub_fields and len(model_field.sub_fields) > 1, "unexpected union subtypes number"

        subfields_kind: List[bool] = []
        for sub_field in model_field.sub_fields:
            shape_type = PydanticShapeType.from_shape(sub_field.shape)
            if shape_type is PydanticShapeType.UNKNOWN:
                raise TypeError(f"fields of type {model_field.type_} are not supported")

            if shape_type in (
                PydanticShapeType.MAPPING,
                PydanticShapeType.HOMOGENEOUS,
                PydanticShapeType.HETEROGENEOUS,
            ):
                raise errors.ModelFieldError(
                    model.__name__, model_field.name, "union type can't be of collection or mapping type",
                )

            subfield_type = sub_field.type_
            if is_xml_model(subfield_type):
                is_model_field = True
            else:
                is_model_field = False

            subfields_kind.append(is_model_field)

        if len(set(subfields_kind)) > 1:
            raise TypeError("unions of combined primitive and model types are not supported")

        is_model_field = subfields_kind[0]
        if is_model_field:
            return cls.ModelSerializer(model, model_field, ctx)
        else:
            return cls.PrimitiveTypeSerializer(model, model_field, ctx)
