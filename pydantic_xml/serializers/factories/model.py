from typing import Any, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.backend import create_element, etree
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Location, Serializer, is_empty, is_xml_model
from pydantic_xml.utils import QName, merge_nsmaps


class ModelSerializerFactory:
    """
    Model serializer factory.
    """

    class RootSerializer(Serializer):
        def __init__(self, model: Type['pxml.BaseXmlModel']):
            name = model.__xml_tag__ or model.__name__
            ns = model.__xml_ns__
            nsmap = model.__xml_nsmap__
            is_root = model.__custom_root_type__

            self._model = model
            self._nsmap = nsmap
            self._is_root = is_root
            self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

            ctx = Serializer.Context(
                parent_ns=ns,
                parent_nsmap=nsmap,
                parent_is_root=is_root,
            )
            self._field_serializers = {
                model_subfield.alias: self._build_field_serializer(model, model_subfield, ctx)
                for field_name, model_subfield in model.__fields__.items()
            }

        @property
        def element_name(self) -> str:
            return self._element_name

        def serialize(
                self, element: Optional[etree.Element], value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return None

            if element is None:
                element = create_element(self._element_name, nsmap=self._nsmap)

            for field_name, field_serializer in self._field_serializers.items():
                field_serializer.serialize(element, getattr(value, field_name), encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: Optional[etree.Element]) -> Optional['pxml.BaseXmlModel']:
            if element is None:
                return None

            result = {
                field_name: field_value
                for field_name, field_serializer in self._field_serializers.items()
                if (field_value := field_serializer.deserialize(element)) is not None
            }
            if self._is_root:
                obj = result['__root__']
            else:
                obj = result

            return self._model.parse_obj(obj)

    class DeferredSerializer(Serializer):

        def __init__(self, model_field: pd.fields.ModelField):
            assert is_xml_model(model_field.type_), "unexpected model field type"
            self._model: Type[pxml.BaseXmlModel] = model_field.type_

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            assert self._model.__xml_serializer__ is not None, "model is partially initialized"

            return self._model.__xml_serializer__.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

        def deserialize(self, element: Optional[etree.Element]) -> Optional['pxml.BaseXmlModel']:
            assert self._model.__xml_serializer__ is not None, "model is partially initialized"

            return self._model.__xml_serializer__.deserialize(element)

    class ElementSerializer(DeferredSerializer):

        def __init__(
                self,
                root_model: Type['pxml.BaseXmlModel'],
                model_field: pd.fields.ModelField,
                ctx: Serializer.Context,
        ):
            super().__init__(model_field)
            name, ns, nsmap = self._get_entity_info(model_field)
            field_name = model_field.alias

            model = self._model
            name = name or model.__xml_tag__ or field_name or model.__name__
            ns = ns or model.__xml_ns__
            nsmap = merge_nsmaps(nsmap, model.__xml_nsmap__, root_model.__xml_nsmap__, ctx.parent_nsmap)

            self._nsmap = nsmap
            self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri

        def serialize(
                self, element: etree.Element, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[etree.Element]:
            if value is None:
                return None

            sub_element = create_element(self._element_name, nsmap=self._nsmap)
            super().serialize(sub_element, value, encoder=encoder, skip_empty=skip_empty)
            if skip_empty and is_empty(sub_element):
                return None
            else:
                element.append(sub_element)
                return sub_element

        def deserialize(self, element: Optional[etree.Element]) -> Optional['pxml.BaseXmlModel']:
            if element is not None and (sub_element := element.find(self._element_name)) is not None:
                return super().deserialize(sub_element)
            else:
                return None

    @classmethod
    def build_root(cls, model: Type['pxml.BaseXmlModel']) -> 'RootSerializer':
        return cls.RootSerializer(model)

    @classmethod
    def build(
            cls,
            model: Type['pxml.BaseXmlModel'],
            model_field: pd.fields.ModelField,
            field_location: Location,
            ctx: Serializer.Context,
    ) -> 'Serializer':
        if field_location is Location.ELEMENT:
            return cls.ElementSerializer(model, model_field, ctx)
        elif not ctx.parent_is_root and field_location is Location.MISSING:
            return cls.ElementSerializer(model, model_field, ctx)
        elif ctx.parent_is_root and field_location is Location.MISSING:
            return cls.DeferredSerializer(model_field)
        elif field_location is Location.ATTRIBUTE:
            raise errors.ModelFieldError(
                model.__name__, model_field.name, "attributes of model type are not supported",
            )
        else:
            raise AssertionError("unreachable")
