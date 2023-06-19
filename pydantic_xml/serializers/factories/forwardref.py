from typing import Any, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Serializer


class ForwardRefSerializerFactory:
    """
    Primitive type serializer factory.
    """

    class ForwardRefSerializer(Serializer):
        def __init__(
                self,
                model: Type['pxml.BaseXmlModel'],
                model_field: pd.fields.ModelField,
                ctx: Serializer.Context,
        ):
            self._model = model
            self._model_field = model_field
            self._ctx = ctx

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            raise pxml.errors.ModelFieldError(
                self._model.__name__,
                self._model_field.name,
                "field is not yet prepared so type is still a ForwardRef, you might need to call update_forward_refs()",
            )

        def deserialize(self, element: Optional[XmlElementReader]) -> Any:
            raise pxml.errors.ModelFieldError(
                self._model.__name__,
                self._model_field.name,
                "field is not yet prepared so type is still a ForwardRef, you might need to call update_forward_refs()",
            )

        def resolve_forward_refs(self) -> Serializer:
            return self._build_field_serializer(self._model, self._model_field, self._ctx)

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        return cls.ForwardRefSerializer(model, model_field, ctx)
