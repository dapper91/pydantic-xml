import dataclasses as dc
import typing
from typing import Any, Optional, Sized, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Serializer, SubFieldWrapper
from pydantic_xml.utils import QName, merge_nsmaps


class WrappedSerializerFactory:
    """
    Wrapped serializer factory.
    """

    class ElementPathSerializer(Serializer):
        def __init__(
                self, model: Type['pxml.BaseXmlModel'], model_field: pd.fields.ModelField, ctx: Serializer.Context,
        ):
            path, ns, nsmap = self._get_entity_info(model_field)
            ns = ns or ctx.parent_ns
            self._nsmap = nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)
            self._search_mode = ctx.search_mode

            field_info = model_field.field_info

            assert path is not None, "path is not provided"
            assert isinstance(field_info, pxml.XmlWrapperInfo), "unexpected field info type"

            # copy field_info from wrapped entity
            model_field = typing.cast(
                pd.fields.ModelField,
                SubFieldWrapper(
                    model_field.name,
                    model_field.alias,
                    field_info.entity or pd.fields.FieldInfo(),
                    model_field,
                ),
            )

            self._path = tuple(QName.from_alias(tag=part, ns=ns, nsmap=nsmap).uri for part in path.split('/'))
            self._inner_serializer = self._build_field_serializer(
                model,
                model_field,
                ctx=dc.replace(
                    ctx,
                    parent_is_root=False,
                    parent_ns=ns,
                    parent_nsmap=nsmap,
                ),
            )

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None:
                return element

            if skip_empty and isinstance(value, Sized) and len(value) == 0:
                return element

            for part in self._path:
                element = element.find_element_or_create(part, self._search_mode, nsmap=self._nsmap)

            self._inner_serializer.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional[Any]:
            if element is not None and \
                    (sub_element := element.find_sub_element(self._path, self._search_mode)) is not None:
                return self._inner_serializer.deserialize(sub_element)
            else:
                return None

        def resolve_forward_refs(self) -> 'Serializer':
            self._inner_serializer = self._inner_serializer.resolve_forward_refs()

            return self

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        return cls.ElementPathSerializer(model, model_field, ctx)
