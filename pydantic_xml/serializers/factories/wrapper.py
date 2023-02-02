import dataclasses as dc
from copy import deepcopy
from typing import Any, Optional, Sized, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml.backend import etree
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Serializer, find_element_or_create
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
            nsmap = merge_nsmaps(nsmap, ctx.parent_nsmap)

            model_field = deepcopy(model_field)
            field_info = model_field.field_info

            assert path is not None, "path is not provided"
            assert isinstance(field_info, pxml.XmlWrapperInfo), "unexpected field info type"

            # copy field_info from wrapped entity
            model_field.field_info = field_info.entity or pd.fields.FieldInfo()

            self._path = tuple(QName.from_alias(tag=part, ns=ns, nsmap=nsmap).uri for part in path.split('/'))
            self._serializer = self._build_field_serializer(
                model,
                model_field,
                ctx=dc.replace(
                    ctx,
                    parent_is_root=True,
                    parent_ns=ns,
                    parent_nsmap=nsmap,
                ),
            )

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return element

            if skip_empty and isinstance(value, Sized) and len(value) == 0:
                return element

            for part in self._path:
                element = find_element_or_create(element, part)

            self._serializer.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: Optional[etree.Element]) -> Optional[Any]:
            if element is not None and (sub_element := element.find('/'.join(self._path))) is not None:
                return self._serializer.deserialize(sub_element)
            else:
                return None

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        return cls.ElementPathSerializer(model, model_field, ctx)
