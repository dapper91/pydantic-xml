import abc
import typing
from typing import Any, Dict, List, Mapping, Optional, Set, Type, Union

import pydantic as pd
import pydantic_core as pdc
from pydantic_core import core_schema as pcs

import pydantic_xml as pxml
from pydantic_xml import errors, utils
from pydantic_xml.element import XmlElementReader, XmlElementWriter, is_element_nill, make_element_nill
from pydantic_xml.serializers.serializer import SearchMode, Serializer, XmlEntityInfoP
from pydantic_xml.typedefs import EntityLocation, Location, NsMap
from pydantic_xml.utils import QName, merge_nsmaps, select_ns


class BaseModelSerializer(Serializer, abc.ABC):
    @property
    @abc.abstractmethod
    def model(self) -> Type['pxml.BaseXmlModel']: ...

    @property
    @abc.abstractmethod
    def element_name(self) -> str: ...

    @property
    @abc.abstractmethod
    def nsmap(self) -> Optional[NsMap]: ...

    @classmethod
    def _check_extra(cls, error_title: str, element: XmlElementReader) -> None:
        line_errors: List[pdc.InitErrorDetails] = []

        for path, attr, value in element.get_unbound():
            line_errors.append(
                pdc.InitErrorDetails(
                    type=pdc.PydanticCustomError(
                        'extra_forbidden',
                        "[line {sourceline}]: {orig}",
                        {
                            'sourceline': (path or (element,))[-1].get_sourceline(),
                            'orig': "Extra inputs are not permitted",
                        },
                    ),
                    loc=tuple(el.tag for el in path) + ((f"@{attr}",) if attr else ()),
                    input=value,
                ),
            )

        if line_errors:
            raise pd.ValidationError.from_exception_data(title=error_title, line_errors=line_errors)


class ModelSerializer(BaseModelSerializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.ModelSchema, ctx: Serializer.Context) -> 'ModelSerializer':
        model_cls = schema['cls']
        fields_schema = schema['schema']

        if fields_schema['type'] == 'function-before':
            fields_schema = fields_schema['schema']

        assert issubclass(model_cls, pxml.BaseXmlModel), "model class must be a BaseXmlModel subclass"
        assert fields_schema['type'] == 'model-fields', f"unexpected schema type: {fields_schema['type']}"
        fields_schema = typing.cast(pcs.ModelFieldsSchema, fields_schema)

        entity_info: Optional[XmlEntityInfoP]
        fields_serialization_exclude: Set[str] = set()
        fields_validation_aliases: Dict[str, str] = {}
        fields_serializers: Dict[str, Serializer] = {}
        for field_name, model_field in fields_schema['fields'].items():
            if model_field.get('serialization_exclude', False):
                fields_serialization_exclude.add(field_name)

            field_alias = model_field.get('serialization_alias')
            if validation_alias := model_field.get('validation_alias'):
                if isinstance(validation_alias, str):
                    fields_validation_aliases[field_name] = validation_alias

            field_info = model_cls.model_fields[field_name]
            if isinstance(field_info, pxml.model.XmlEntityInfo):
                entity_info = field_info
            else:
                entity_info = None

            field_ctx = ctx.child(
                field_name=field_name,
                field_alias=field_alias,
                entity_info=entity_info,
            )
            fields_serializers[field_name] = Serializer.parse_core_schema(model_field['schema'], field_ctx)

        for model_field in fields_schema['computed_fields']:
            field_name = model_field['property_name']
            field_alias = model_field.get('alias')

            computed_field_info = model_cls.__pydantic_decorators__.computed_fields[field_name].info
            if isinstance(computed_field_info, pxml.model.ComputedXmlEntityInfo):
                entity_info = computed_field_info
            else:
                entity_info = None

            field_ctx = ctx.child(
                field_name=field_name,
                field_alias=field_alias,
                field_computed=True,
                entity_info=entity_info,
            )
            fields_serializers[field_name] = Serializer.parse_core_schema(model_field['return_schema'], field_ctx)

        name = model_cls.__xml_tag__ or model_cls.__name__
        ns = model_cls.__xml_ns__
        nsmap = model_cls.__xml_nsmap__

        return cls(
            model_cls, name, ns, nsmap,
            fields_serializers, fields_validation_aliases, fields_serialization_exclude,
        )

    def __init__(
            self,
            model: Type['pxml.BaseXmlModel'],
            name: str,
            ns: Optional[str],
            nsmap: Optional[NsMap],
            field_serializers: Dict[str, Serializer],
            fields_validation_aliases: Dict[str, str],
            fields_serialization_exclude: Set[str],
    ):

        self._model = model
        self._field_serializers = field_serializers
        self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
        self._nsmap = nsmap
        self._fields_validation_aliases = fields_validation_aliases
        self._fields_serialization_exclude = fields_serialization_exclude

    @property
    def model(self) -> Type['pxml.BaseXmlModel']:
        return self._model

    @property
    def element_name(self) -> str:
        return self._element_name

    @property
    def nsmap(self) -> Optional[NsMap]:
        return self._nsmap

    @property
    def fields_serializers(self) -> Mapping[str, Serializer]:
        return self._field_serializers

    def serialize(
            self,
            element: XmlElementWriter,
            value: 'pxml.BaseXmlModel',
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return None

        if self._model.__xml_skip_empty__ is not None:
            skip_empty = self._model.__xml_skip_empty__

        for field_name, field_serializer in self._field_serializers.items():
            if field_name not in self._fields_serialization_exclude:
                field_serializer.serialize(
                    element, getattr(value, field_name), encoded[field_name], skip_empty=skip_empty,
                )

        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional['pxml.BaseXmlModel']:
        if element is None:
            return None

        result: Dict[str, Any] = {}
        field_errors: Dict[Union[None, str, int], pd.ValidationError] = {}
        for field_name, field_serializer in self._field_serializers.items():
            try:
                loc = (field_name,)
                sourcemap[loc] = element.get_sourceline()
                field_value = field_serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc)
                if field_value is not None:
                    field_name = self._fields_validation_aliases.get(field_name, field_name)
                    result[field_name] = field_value
            except pd.ValidationError as err:
                field_errors[field_name] = err

        if field_errors:
            raise utils.build_validation_error(title=self._model.__name__, errors_map=field_errors)

        if self._model.model_config.get('extra', 'ignore') == 'forbid':
            self._check_extra(self._model.__name__, element)

        try:
            return self._model.model_validate(result, strict=False, context=context)
        except pd.ValidationError as err:
            raise utils.set_validation_error_sourceline(err, sourcemap)


class RootModelSerializer(BaseModelSerializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.ModelSchema, ctx: Serializer.Context) -> 'RootModelSerializer':
        model_cls = schema['cls']
        root_schema = schema['schema']

        assert issubclass(model_cls, pxml.BaseXmlModel), "model class must be a BaseXmlModel subclass"

        entity_info: Optional[XmlEntityInfoP]
        field_info = model_cls.model_fields['root']
        if isinstance(field_info, pxml.model.XmlEntityInfo):
            entity_info = field_info
        else:
            entity_info = None

        field_ctx = ctx.child(
            field_name=None,
            entity_info=entity_info,
        )
        root_serializer = Serializer.parse_core_schema(root_schema, field_ctx)

        name = model_cls.__xml_tag__ or model_cls.__name__
        ns = model_cls.__xml_ns__
        nsmap = model_cls.__xml_nsmap__

        return cls(model_cls, name, ns, nsmap, root_serializer)

    def __init__(
            self,
            model: Type['pxml.BaseXmlModel'],
            name: str,
            ns: Optional[str],
            nsmap: Optional[NsMap],
            root_serializer: Serializer,
    ):

        self._model = model
        self._root_serializer = root_serializer
        self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
        self._nsmap = nsmap

    @property
    def model(self) -> Type['pxml.BaseXmlModel']:
        return self._model

    @property
    def element_name(self) -> str:
        return self._element_name

    @property
    def nsmap(self) -> Optional[NsMap]:
        return self._nsmap

    def serialize(
            self,
            element: XmlElementWriter,
            value: 'pxml.RootXmlModel[Any]',
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        if value is None:
            return None

        if self._model.__xml_skip_empty__ is not None:
            skip_empty = self._model.__xml_skip_empty__

        self._root_serializer.serialize(element, getattr(value, 'root'), encoded, skip_empty=skip_empty)

        return element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional['pxml.BaseXmlModel']:
        if element is None:
            return None

        try:
            result = self._root_serializer.deserialize(element, context=context, sourcemap=sourcemap, loc=loc)
            if result is None:
                result = pdc.PydanticUndefined
        except pd.ValidationError as err:
            raise utils.build_validation_error(title=self._model.__name__, errors_map={None: err})

        if self._model.model_config.get('extra', 'ignore') == 'forbid':
            self._check_extra(self._model.__name__, element)

        try:
            return self._model.model_validate(result, strict=False, context=context)
        except pd.ValidationError as err:
            raise utils.set_validation_error_sourceline(err, sourcemap)


class ModelProxySerializer(BaseModelSerializer):
    @classmethod
    def from_core_schema(cls, schema: pcs.ModelSchema, ctx: Serializer.Context) -> 'ModelProxySerializer':
        model_cls = schema['cls']
        assert issubclass(model_cls, pxml.BaseXmlModel), "unexpected model type"

        name = ctx.entity_path or model_cls.__xml_tag__ or ctx.field_alias or ctx.field_name or model_cls.__name__
        ns = select_ns(ctx.entity_ns, model_cls.__xml_ns__, ctx.parent_ns)
        nsmap = merge_nsmaps(ctx.entity_nsmap, model_cls.__xml_nsmap__, ctx.parent_nsmap)
        search_mode = ctx.search_mode
        computed = ctx.field_computed
        nillable = ctx.nillable

        return cls(model_cls, name, ns, nsmap, search_mode, computed, nillable)

    def __init__(
            self,
            model: Type['pxml.BaseXmlModel'],
            name: str,
            ns: Optional[str],
            nsmap: Optional[NsMap],
            search_mode: SearchMode,
            computed: bool,
            nillable: bool,
    ):
        self._model = model
        self._element_name = QName.from_alias(tag=name, ns=ns, nsmap=nsmap).uri
        self._nsmap = nsmap
        self._search_mode = search_mode
        self._computed = computed
        self._nillable = nillable

    @property
    def model(self) -> Type['pxml.BaseXmlModel']:
        return self._model

    @property
    def model_serializer(self) -> Optional[BaseModelSerializer]:
        return self._model.__xml_serializer__

    @property
    def element_name(self) -> str:
        return self._element_name

    @property
    def nsmap(self) -> Optional[NsMap]:
        return self._nsmap

    def serialize(
            self,
            element: XmlElementWriter,
            value: 'pxml.BaseXmlModel',
            encoded: Dict[str, Any],
            *,
            skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        assert self._model.__xml_serializer__ is not None, f"model {self._model.__name__} is partially initialized"

        if self._nillable and value is None:
            sub_element = element.make_element(self._element_name, nsmap=self._nsmap)
            make_element_nill(sub_element)
            element.append_element(sub_element)
            return sub_element

        if value is None:
            return None

        sub_element = element.make_element(self._element_name, nsmap=self._nsmap)
        self._model.__xml_serializer__.serialize(sub_element, value, encoded, skip_empty=skip_empty)
        if skip_empty and sub_element.is_empty():
            return None
        else:
            element.append_element(sub_element)
            return sub_element

    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional['pxml.BaseXmlModel']:
        assert self._model.__xml_serializer__ is not None, f"model {self._model.__name__} is partially initialized"

        if self._computed:
            return None

        if element is None:
            return None

        if (sub_element := element.pop_element(self._element_name, self._search_mode)) is not None:
            sourcemap[loc] = sub_element.get_sourceline()
            if is_element_nill(sub_element):
                return None
            else:
                return self._model.__xml_serializer__.deserialize(
                    sub_element, context=context, sourcemap=sourcemap, loc=loc,
                )
        else:
            return None


def from_core_schema(schema: pcs.ModelSchema, ctx: Serializer.Context) -> Serializer:
    is_root_model = schema['root_model']

    if ctx.top:
        if is_root_model:
            return RootModelSerializer.from_core_schema(schema, ctx)
        else:
            return ModelSerializer.from_core_schema(schema, ctx)

    else:
        if ctx.entity_location in (EntityLocation.ELEMENT, None):
            if is_root_model:
                return ModelProxySerializer.from_core_schema(schema, ctx)
            else:
                return ModelProxySerializer.from_core_schema(schema, ctx)
        elif ctx.entity_location is EntityLocation.ATTRIBUTE:
            raise errors.ModelFieldError(ctx.model_name, ctx.field_name, "attributes of a model type are not supported")
        else:
            raise AssertionError("unreachable")
