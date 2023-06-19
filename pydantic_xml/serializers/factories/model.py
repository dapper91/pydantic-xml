import abc
from typing import Any, Optional, Type

import pydantic as pd

import pydantic_xml as pxml
from pydantic_xml import errors
from pydantic_xml.element import XmlElementReader, XmlElementWriter
from pydantic_xml.serializers.encoder import XmlEncoder
from pydantic_xml.serializers.serializer import Location, Serializer, is_xml_model
from pydantic_xml.typedefs import NsMap
from pydantic_xml.utils import QName, merge_nsmaps


class ModelSerializerFactory:
    """
    Model serializer factory.
    """

    class ModelSerializer(Serializer):
        @property
        @abc.abstractmethod
        def model(self) -> Type['pxml.BaseXmlModel']:
            pass

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
                search_mode=model.__xml_search_mode__,
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

        @property
        def nsmap(self) -> Optional[NsMap]:
            return self._nsmap

        @property
        def model(self) -> Type['pxml.BaseXmlModel']:
            return self._model

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None:
                return None

            for field_name, field_serializer in self._field_serializers.items():
                field_serializer.serialize(element, getattr(value, field_name), encoder=encoder, skip_empty=skip_empty)

            return element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional['pxml.BaseXmlModel']:
            if element is None:
                return None

            result = {
                field_name: field_value
                for field_name, field_serializer in self._field_serializers.items()
                if (field_value := field_serializer.deserialize(element)) is not None
            }
            if self._is_root:
                obj = result.get('__root__')
            else:
                obj = result

            return self._model.parse_obj(obj)

        def resolve_forward_refs(self) -> 'Serializer':
            self._field_serializers = {
                field_name: serializer.resolve_forward_refs()
                for field_name, serializer in self._field_serializers.items()
            }

            return self

    class DeferredSerializer(ModelSerializer):

        def __init__(self, model_field: pd.fields.ModelField):
            assert is_xml_model(model_field.type_), "unexpected model field type"
            self._model: Type[pxml.BaseXmlModel] = model_field.type_

        @property
        def model(self) -> Type['pxml.BaseXmlModel']:
            return self._model

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            assert self._model.__xml_serializer__ is not None, f"model {self._model.__name__} is partially initialized"

            return self._model.__xml_serializer__.serialize(element, value, encoder=encoder, skip_empty=skip_empty)

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional['pxml.BaseXmlModel']:
            assert self._model.__xml_serializer__ is not None, f"model {self._model.__name__} is partially initialized"

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
            self._search_mode = ctx.search_mode

        def serialize(
                self, element: XmlElementWriter, value: Any, *, encoder: XmlEncoder, skip_empty: bool = False,
        ) -> Optional[XmlElementWriter]:
            if value is None:
                return None

            sub_element = element.make_element(self._element_name, nsmap=self._nsmap)
            super().serialize(sub_element, value, encoder=encoder, skip_empty=skip_empty)
            if skip_empty and sub_element.is_empty():
                return None
            else:
                element.append_element(sub_element)
                return sub_element

        def deserialize(self, element: Optional[XmlElementReader]) -> Optional['pxml.BaseXmlModel']:
            if element is not None and \
                    (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
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
