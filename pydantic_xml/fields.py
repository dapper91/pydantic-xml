import dataclasses as dc
import typing
from typing import Any, Callable, Dict, Optional, Union

import pydantic as pd
import pydantic_core as pdc

from . import compat, config, model, utils
from .typedefs import EntityLocation
from .utils import NsMap

__all__ = (
    'attr',
    'computed_attr',
    'computed_element',
    'computed_entity',
    'element',
    'extract_field_xml_entity_info',
    'wrapped',
    'xml_field_serializer',
    'xml_field_validator',
    'ComputedXmlEntityInfo',
    'XmlEntityInfo',
    'XmlEntityInfoP',
    'XmlFieldSerializer',
    'XmlFieldValidator',
)


class XmlEntityInfoP(typing.Protocol):
    location: Optional[EntityLocation]
    path: Optional[str]
    ns: Optional[str]
    nsmap: Optional[NsMap]
    nillable: Optional[bool]
    wrapped: Optional['XmlEntityInfoP']


@dc.dataclass(frozen=True)
class XmlEntityInfo(XmlEntityInfoP):
    """
    Field xml meta-information.
    """

    location: Optional[EntityLocation]
    path: Optional[str] = None
    ns: Optional[str] = None
    nsmap: Optional[NsMap] = None
    nillable: Optional[bool] = None
    wrapped: Optional[XmlEntityInfoP] = None

    def __post_init__(self) -> None:
        if config.REGISTER_NS_PREFIXES and self.nsmap:
            utils.register_nsmap(self.nsmap)

    @staticmethod
    def merge(*entity_infos: XmlEntityInfoP) -> 'XmlEntityInfo':
        location: Optional[EntityLocation] = None
        path: Optional[str] = None
        ns: Optional[str] = None
        nsmap: Optional[NsMap] = None
        nillable: Optional[bool] = None
        wrapped: Optional[XmlEntityInfoP] = None

        for entity_info in entity_infos:
            if entity_info.location is not None:
                location = entity_info.location
            if entity_info.wrapped is not None:
                wrapped = entity_info.wrapped
            if entity_info.path is not None:
                path = entity_info.path
            if entity_info.ns is not None:
                ns = entity_info.ns
            if entity_info.nsmap is not None:
                nsmap = utils.merge_nsmaps(entity_info.nsmap, nsmap)
            if entity_info.nillable is not None:
                nillable = entity_info.nillable

        return XmlEntityInfo(
            location=location,
            path=path,
            ns=ns,
            nsmap=nsmap,
            nillable=nillable,
            wrapped=wrapped,
        )


def extract_field_xml_entity_info(field_info: pd.fields.FieldInfo) -> Optional[XmlEntityInfoP]:
    entity_info_list = list(filter(lambda meta: isinstance(meta, XmlEntityInfo), field_info.metadata))
    if entity_info_list:
        entity_info = XmlEntityInfo.merge(*entity_info_list)
    else:
        entity_info = None

    return entity_info


_Unset: Any = pdc.PydanticUndefined


def prepare_field_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    if kwargs.get('serialization_alias') in (None, pdc.PydanticUndefined):
        kwargs['serialization_alias'] = kwargs.get('alias')

    if kwargs.get('validation_alias') in (None, pdc.PydanticUndefined):
        kwargs['validation_alias'] = kwargs.get('alias')

    return kwargs


def attr(
        name: Optional[str] = None,
        ns: Optional[str] = None,
        *,
        default: Any = pdc.PydanticUndefined,
        default_factory: Optional[Callable[[], Any]] = _Unset,
        **kwargs: Any,
) -> Any:
    """
    Marks a pydantic field as an xml attribute.

    :param name: attribute name
    :param ns: attribute xml namespace
    :param default: the default value of the field.
    :param default_factory: the factory function used to construct the default for the field.
    :param kwargs: pydantic field arguments. See :py:class:`pydantic.Field`
    """

    kwargs = prepare_field_kwargs(kwargs)

    field_info = pd.fields.FieldInfo(default=default, default_factory=default_factory, **kwargs)
    field_info.metadata.append(
        XmlEntityInfo(EntityLocation.ATTRIBUTE, path=name, ns=ns),
    )

    return field_info


def element(
        tag: Optional[str] = None,
        ns: Optional[str] = None,
        nsmap: Optional[NsMap] = None,
        nillable: Optional[bool] = None,
        *,
        default: Any = pdc.PydanticUndefined,
        default_factory: Optional[Callable[[], Any]] = _Unset,
        **kwargs: Any,
) -> Any:
    """
    Marks a pydantic field as an xml element.

    :param tag: element tag
    :param ns: element xml namespace
    :param nsmap: element xml namespace map
    :param nillable: is element nillable. See https://www.w3.org/TR/xmlschema-1/#xsi_nil.
    :param default: the default value of the field.
    :param default_factory: the factory function used to construct the default for the field.
    :param kwargs: pydantic field arguments. See :py:class:`pydantic.Field`
    """

    kwargs = prepare_field_kwargs(kwargs)

    field_info = pd.fields.FieldInfo(default=default, default_factory=default_factory, **kwargs)
    field_info.metadata.append(
        XmlEntityInfo(EntityLocation.ELEMENT, path=tag, ns=ns, nsmap=nsmap, nillable=nillable),
    )

    return field_info


def wrapped(
        path: str,
        entity: Optional[pd.fields.FieldInfo] = None,
        ns: Optional[str] = None,
        nsmap: Optional[NsMap] = None,
        *,
        default: Any = pdc.PydanticUndefined,
        default_factory: Optional[Callable[[], Any]] = _Unset,
        **kwargs: Any,
) -> Any:
    """
    Marks a pydantic field as a wrapped xml entity.

    :param entity: wrapped entity
    :param path: entity path
    :param ns: element xml namespace
    :param nsmap: element xml namespace map
    :param default: the default value of the field.
    :param default_factory: the factory function used to construct the default for the field.
    :param kwargs: pydantic field arguments. See :py:class:`pydantic.Field`
    """

    if entity is None:
        wrapped_entity_info = None
        field_info = pd.fields.FieldInfo(default=default, default_factory=default_factory, **kwargs)
    else:
        wrapped_entity_info = extract_field_xml_entity_info(entity)
        field_info = compat.merge_field_infos(
            pd.fields.FieldInfo(default=default, default_factory=default_factory, **kwargs),
            entity,
        )

    field_info.metadata.append(
        XmlEntityInfo(EntityLocation.WRAPPED, path=path, ns=ns, nsmap=nsmap, wrapped=wrapped_entity_info),
    )

    return field_info


@dc.dataclass
class ComputedXmlEntityInfo(pd.fields.ComputedFieldInfo, XmlEntityInfoP):
    """
    Computed field xml meta-information.
    """

    __slots__ = ('location', 'path', 'ns', 'nsmap', 'nillable', 'wrapped')

    location: Optional[EntityLocation]
    path: Optional[str]
    ns: Optional[str]
    nsmap: Optional[NsMap]
    nillable: Optional[bool]
    wrapped: Optional[XmlEntityInfoP]  # to be compliant with XmlEntityInfoP protocol

    def __post_init__(self) -> None:
        if config.REGISTER_NS_PREFIXES and self.nsmap:
            utils.register_nsmap(self.nsmap)


PropertyT = typing.TypeVar('PropertyT')


def computed_entity(
        location: EntityLocation,
        prop: Optional[PropertyT] = None,
        **kwargs: Any,
) -> Union[PropertyT, Callable[[PropertyT], PropertyT]]:
    def decorator(prop: Any) -> Any:
        path = kwargs.pop('path', None)
        ns = kwargs.pop('ns', None)
        nsmap = kwargs.pop('nsmap', None)
        nillable = kwargs.pop('nillable', None)

        descriptor_proxy = pd.computed_field(**kwargs)(prop)
        descriptor_proxy.decorator_info = ComputedXmlEntityInfo(
            location=location,
            path=path,
            ns=ns,
            nsmap=nsmap,
            nillable=nillable,
            wrapped=None,
            **dc.asdict(descriptor_proxy.decorator_info),
        )

        return descriptor_proxy

    if prop is None:
        return decorator
    else:
        return decorator(prop)


def computed_attr(
        prop: Optional[PropertyT] = None,
        *,
        name: Optional[str] = None,
        ns: Optional[str] = None,
        **kwargs: Any,
) -> Union[PropertyT, Callable[[PropertyT], PropertyT]]:
    """
    Marks a property as an xml attribute.

    :param prop: decorated property
    :param name: attribute name
    :param ns: attribute xml namespace
    :param kwargs: pydantic computed field arguments. See :py:class:`pydantic.computed_field`
    """

    return computed_entity(EntityLocation.ATTRIBUTE, prop, path=name, ns=ns, **kwargs)


def computed_element(
        prop: Optional[PropertyT] = None,
        *,
        tag: Optional[str] = None,
        ns: Optional[str] = None,
        nsmap: Optional[NsMap] = None,
        nillable: Optional[bool] = None,
        **kwargs: Any,
) -> Union[PropertyT, Callable[[PropertyT], PropertyT]]:
    """
    Marks a property as an xml element.

    :param prop: decorated property
    :param tag: element tag
    :param ns: element xml namespace
    :param nsmap: element xml namespace map
    :param nillable: is element nillable. See https://www.w3.org/TR/xmlschema-1/#xsi_nil.
    :param kwargs: pydantic computed field arguments. See :py:class:`pydantic.computed_field`
    """

    return computed_entity(EntityLocation.ELEMENT, prop, path=tag, ns=ns, nsmap=nsmap, nillable=nillable, **kwargs)


def xml_field_validator(
    field: str, /, *fields: str,
) -> 'Callable[[model.ValidatorFuncT[model.ModelT]], model.ValidatorFuncT[model.ModelT]]':
    """
    Marks the method as a field xml validator.

    :param field: field to be validated
    :param fields: fields to be validated
    """

    def wrapper(func: model.ValidatorFuncT[model.ModelT]) -> model.ValidatorFuncT[model.ModelT]:
        if isinstance(func, (classmethod, staticmethod)):
            func = func.__func__
        setattr(func, '__xml_field_validator__', (field, *fields))
        return func

    return wrapper


def xml_field_serializer(
    field: str, /, *fields: str,
) -> 'Callable[[model.SerializerFuncT[model.ModelT]], model.SerializerFuncT[model.ModelT]]':
    """
    Marks the method as a field xml serializer.

    :param field: field to be serialized
    :param fields: fields to be serialized
    """

    def wrapper(func: model.SerializerFuncT[model.ModelT]) -> model.SerializerFuncT[model.ModelT]:
        setattr(func, '__xml_field_serializer__', (field, *fields))
        return func

    return wrapper


@dc.dataclass(frozen=True)
class XmlFieldValidator:
    func: 'model.ValidatorFunc'


@dc.dataclass(frozen=True)
class XmlFieldSerializer:
    func: 'model.SerializerFunc'
