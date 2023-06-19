import dataclasses as dc
import typing
from typing import Any, List, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Location, PydanticShapeType, Serializer, SubFieldWrapper
from pydantic_xml.utils import QName, merge_nsmaps


class HeterogeneousSerializerFactory:
    """
    Heterogeneous collection type serializer factory.
    """

    class ElementSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            assert model_field.sub_fields is not None, "unexpected model field"

            name, ns, nsmap = self._get_entity_info(model_field)
            name = name or model_field.alias
            ns = ns or ctx.parent_ns
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

            self._inner_serializers = []
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

                self._inner_serializers.append(
                    self._build_field_serializer(
                        model,
                        sub_field,
                        dc.replace(
                            ctx,
                            parent_is_root=False,
                            parent_ns=ns,
                            parent_nsmap=nsmap,
                        ),
                    ),
                )

        def resolve_forward_refs(self) -> 'Serializer':
            self._inner_serializers = [
                serializer.resolve_forward_refs()
                for serializer in self._inner_serializers
            ]

            return self

        def serialize(
                self, element: XmlElementWriter, value: List[Any], *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None:
                return element

            if skip_empty and len(value) == 0:
                return element

            for serializer, val in zip(self._inner_serializers, value):
                if skip_empty and val is None:
                    continue

                serializer.serialize(element, val, encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[List[Any]]:
            if element is None:
                return None

            return [
                serializer.deserialize(element)
                for serializer in self._inner_serializers
            ]

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        assert model_field.sub_fields is not None, "unexpected model field"

        is_root = model.__custom_root_type__

        for item_field in model_field.sub_fields:
            if PydanticShapeType.from_shape(item_field.shape) in (
                PydanticShapeType.HOMOGENEOUS,
                PydanticShapeType.HETEROGENEOUS,
            ):
                raise errors.ModelFieldError(
                    model.__name__, model_field.name, "collection elements can't be of collection type",
                )

            if is_root and field_location is Location.MISSING:
                raise errors.ModelFieldError(
                    model.__name__, model_field.name, "root model collections should be marked as elements",
                )

        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "attributes of collection type are not supported",
            )
        else:
            raise AssertionError("unreachable")
