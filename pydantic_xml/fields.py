import dataclasses as dc
import typing
from typing import Any, Callable, Optional, Union

import pydantic as pd
import pydantic_core as pdc
from pydantic._internal._model_construction import ModelMetaclass  # noqa
from pydantic.root_model import _RootModelMetaclass as RootModelMetaclass  # noqa

from . import config, model, utils
from .typedefs import EntityLocation
from .utils import NsMap

__all__ = (
    'attr',
    'computed_attr',
    'computed_element',
    'computed_entity',
    'element',
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


class XmlEntityInfo(pd.fields.FieldInfo, XmlEntityInfoP):
    """
    Field xml meta-information.
    """

    __slots__ = ('location', 'path', 'ns', 'nsmap', 'nillable', 'wrapped')

    @staticmethod
    def merge_field_infos(*field_infos: pd.fields.FieldInfo, **overrides: Any) -> pd.fields.FieldInfo:
        location, path, ns, nsmap, nillable, wrapped = None, None, None, None, None, None

        for field_info in field_infos:
            if isinstance(field_info, XmlEntityInfo):
                location = field_info.location if field_info.location is not None else location
                path = field_info.path if field_info.path is not None else path
                ns = field_info.ns if field_info.ns is not None else ns
                nsmap = field_info.nsmap if field_info.nsmap is not None else nsmap
                nillable = field_info.nillable if field_info.nillable is not None else nillable
                wrapped = field_info.wrapped if field_info.wrapped is not None else wrapped

        field_info = pd.fields.FieldInfo.merge_field_infos(*field_infos, **overrides)

        xml_entity_info = XmlEntityInfo(
            location,
            path=path,
            ns=ns,
            nsmap=nsmap,
            nillable=nillable,
            wrapped=wrapped if isinstance(wrapped, XmlEntityInfo) else None,
            **field_info._attributes_set,
        )
        xml_entity_info.metadata = field_info.metadata

        return xml_entity_info

    def __init__(
            self,
            location: Optional[EntityLocation],
            /,
            path: Optional[str] = None,
            ns: Optional[str] = None,
            nsmap: Optional[NsMap] = None,
            nillable: Optional[bool] = None,
            wrapped: Optional[pd.fields.FieldInfo] = None,
            **kwargs: Any,
    ):
        wrapped_metadata: list[Any] = []
        if wrapped is not None:
            # copy arguments from the wrapped entity to let pydantic know how to process the field
            for entity_field_name in utils.get_slots(wrapped):
                if entity_field_name in pd.fields._FIELD_ARG_NAMES:
                    kwargs[entity_field_name] = getattr(wrapped, entity_field_name)
            wrapped_metadata = wrapped.metadata

        if kwargs.get('serialization_alias') is None:
            kwargs['serialization_alias'] = kwargs.get('alias')

        if kwargs.get('validation_alias') is None:
            kwargs['validation_alias'] = kwargs.get('alias')

        super().__init__(**kwargs)
        self.metadata.extend(wrapped_metadata)

        self.location = location
        self.path = path
        self.ns = ns
        self.nsmap = nsmap
        self.nillable = nillable
        self.wrapped: Optional[XmlEntityInfoP] = wrapped if isinstance(wrapped, XmlEntityInfo) else None

        if config.REGISTER_NS_PREFIXES and nsmap:
            utils.register_nsmap(nsmap)


_Unset: Any = pdc.PydanticUndefined


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

    return XmlEntityInfo(
        EntityLocation.ATTRIBUTE,
        path=name, ns=ns, default=default, default_factory=default_factory,
        **kwargs,
    )


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

    return XmlEntityInfo(
        EntityLocation.ELEMENT,
        path=tag, ns=ns, nsmap=nsmap, nillable=nillable, default=default, default_factory=default_factory,
        **kwargs,
    )


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

    return XmlEntityInfo(
        EntityLocation.WRAPPED,
        path=path, ns=ns, nsmap=nsmap, wrapped=entity, default=default, default_factory=default_factory,
        **kwargs,
    )


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
    field: str, /, *fields: str
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
    field: str, /, *fields: str
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
