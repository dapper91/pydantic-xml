import typing
from typing import Any, ClassVar, Dict, Generic, Optional, Tuple, Type, TypeVar, Union

import pydantic as pd
import pydantic_core as pdc
import typing_extensions as te
from pydantic import BaseModel, RootModel
from pydantic._internal._model_construction import ModelMetaclass  # noqa
from pydantic.root_model import _RootModelMetaclass as RootModelMetaclass  # noqa

from . import config, errors, utils
from .element import SearchMode
from .element.native import ElementT, XmlElement, etree
from .fields import SerializerFunc, ValidatorFunc, XmlEntityInfo, XmlFieldSerializer, XmlFieldValidator, attr, element
from .fields import wrapped
from .serializers.factories.model import BaseModelSerializer
from .serializers.serializer import Serializer
from .typedefs import EntityLocation
from .utils import NsMap

__all__ = (
    'BaseXmlModel',
    'create_model',
    'RootXmlModel',
    'XmlModelMeta',
)


Model = TypeVar('Model', bound='BaseXmlModel')


def create_model(
        __model_name: str,
        *,
        __tag__: Optional[str] = None,
        __ns__: Optional[str] = None,
        __nsmap__: Optional[NsMap] = None,
        __ns_attrs__: Optional[bool] = None,
        __skip_empty__: Optional[bool] = None,
        __search_mode__: Optional[SearchMode] = None,
        __base__: Union[Type[Model], Tuple[Type[Model], ...], None] = None,
        __module__: Optional[str] = None,
        **kwargs: Any,
) -> Type[Model]:
    """
    Dynamically creates a new pydantic-xml model.

    :param __model_name: model name
    :param __tag__: element tag
    :param __ns__: element namespace
    :param __nsmap__: element namespace map
    :param __ns_attrs__: use namespaced attributes
    :param __skip_empty__: skip empty elements (elements without sub-elements, attributes and text)
    :param __search_mode__: element search mode
    :param __base__: model base class
    :param __module__: module name that the model belongs to
    :param kwargs: pydantic model creation arguments.
                   See https://docs.pydantic.dev/latest/api/base_model/#pydantic.create_model.

    :return: created model
    """

    cls_kwargs = kwargs.setdefault('__cls_kwargs__', {})
    cls_kwargs['metaclass'] = XmlModelMeta

    cls_kwargs['tag'] = __tag__
    cls_kwargs['ns'] = __ns__
    cls_kwargs['nsmap'] = __nsmap__
    cls_kwargs['ns_attrs'] = __ns_attrs__
    cls_kwargs['skip_empty'] = __skip_empty__
    cls_kwargs['search_mode'] = __search_mode__

    model_base: Union[Type[BaseModel], Tuple[Type[BaseModel], ...]] = __base__ or BaseXmlModel

    if model_config := kwargs.pop('__config__', None):
        # since pydantic create_model function forbids __base__ and __config__ arguments together,
        # we create base pydantic class with __config__ and inherit from it
        BaseWithConfig = pd.create_model(
            f'{__model_name}Base',
            __module__=__module__,  # type: ignore[arg-type]
            __config__=model_config,
        )
        if not isinstance(model_base, tuple):
            model_base = (model_base, BaseWithConfig)
        else:
            model_base = (*model_base, BaseWithConfig)

    model = pd.create_model(__model_name, __base__=model_base, **kwargs)

    return typing.cast(Type[Model], model)


@te.dataclass_transform(kw_only_default=True, field_specifiers=(attr, element, wrapped, pd.Field))
class XmlModelMeta(ModelMetaclass):
    """
    Xml model metaclass.
    """

    def __new__(
            mcls,
            name: str,
            bases: Tuple[type],
            namespace: Dict[str, Any],
            **kwargs: Any,
    ) -> Type['BaseXmlModel']:
        is_abstract: bool = kwargs.pop('__xml_abstract__', False)

        cls = typing.cast(Type['BaseXmlModel'], super().__new__(mcls, name, bases, namespace, **kwargs))
        if not is_abstract:
            cls.__build_serializer__()

        cls._collect_xml_field_serializers_validators(cls)

        return cls

    @classmethod
    def _collect_xml_field_serializers_validators(mcls, cls: Type['BaseXmlModel']) -> None:
        for field_name, field_info in cls.model_fields.items():
            for metadatum in field_info.metadata:
                if isinstance(metadatum, XmlFieldValidator):
                    cls.__xml_field_validators__[field_name] = metadatum.func
                if isinstance(metadatum, XmlFieldSerializer):
                    cls.__xml_field_serializers__[field_name] = metadatum.func

        # find custom validators/serializers in all defined attributes
        # though we want to skip any BaseModel attributes, as these can never be field
        # serializers/validators, and getting certain pydantic fields
        # may cause recursion errors for recursive / self-referential models
        for attr_name in set(dir(cls)) - set(dir(BaseModel)):
            if func := getattr(cls, attr_name, None):
                if fields := getattr(func, '__xml_field_serializer__', None):
                    for field in fields:
                        cls.__xml_field_serializers__[field] = func
                if fields := getattr(func, '__xml_field_validator__', None):
                    for field in fields:
                        cls.__xml_field_validators__[field] = func


ModelT = TypeVar('ModelT', bound='BaseXmlModel')


class BaseXmlModel(BaseModel, __xml_abstract__=True, metaclass=XmlModelMeta):
    """
    Base pydantic-xml model.
    """

    __xml_tag__: ClassVar[Optional[str]]
    __xml_ns__: ClassVar[Optional[str]]
    __xml_nsmap__: ClassVar[Optional[NsMap]]
    __xml_ns_attrs__: ClassVar[bool]
    __xml_skip_empty__: ClassVar[Optional[bool]]
    __xml_search_mode__: ClassVar[SearchMode]
    __xml_serializer__: ClassVar[Optional[BaseModelSerializer]] = None

    __xml_field_validators__: ClassVar[Dict[str, ValidatorFunc]] = {}
    __xml_field_serializers__: ClassVar[Dict[str, SerializerFunc]] = {}

    def __init_subclass__(
            cls,
            tag: Optional[str] = None,
            ns: Optional[str] = None,
            nsmap: Optional[NsMap] = None,
            ns_attrs: Optional[bool] = None,
            skip_empty: Optional[bool] = None,
            search_mode: Optional[SearchMode] = None,
            **kwargs: Any,
    ):
        """
        Initializes a subclass.

        :param tag: element tag
        :param ns: element namespace
        :param nsmap: element namespace map
        :param ns_attrs: use namespaced attributes
        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text)
        :param search_mode: element search mode
        """

        super().__init_subclass__(**kwargs)

        cls.__xml_tag__ = tag if tag is not None else getattr(cls, '__xml_tag__', None)
        cls.__xml_ns__ = ns if ns is not None else getattr(cls, '__xml_ns__', None)
        cls.__xml_ns_attrs__ = ns_attrs if ns_attrs is not None else getattr(cls, '__xml_ns_attrs__', False)
        cls.__xml_skip_empty__ = skip_empty if skip_empty is not None else getattr(cls, '__xml_skip_empty__', None)
        cls.__xml_search_mode__ = search_mode if search_mode is not None \
            else getattr(cls, '__xml_search_mode__', SearchMode.STRICT)

        if parent_nsmap := getattr(cls, '__xml_nsmap__', None):
            parent_nsmap.update(nsmap or {})
            cls.__xml_nsmap__ = parent_nsmap
        else:
            cls.__xml_nsmap__ = nsmap

        cls.__xml_field_serializers__ = {}
        cls.__xml_field_validators__ = {}

    @classmethod
    def __build_serializer__(cls) -> None:
        if cls is BaseXmlModel:
            return

        # checks that all generic parameters are provided
        if cls.__pydantic_root_model__:
            if cls.__pydantic_generic_metadata__['parameters']:
                if cls.model_fields.get('root') is None or isinstance(cls.model_fields['root'].annotation, TypeVar):
                    cls.__xml_serializer__ = None
                    return
        else:
            if cls.__pydantic_generic_metadata__['parameters']:
                cls.__xml_serializer__ = None
                return

        if config.REGISTER_NS_PREFIXES and cls.__xml_nsmap__:
            utils.register_nsmap(cls.__xml_nsmap__)

        if cls.__pydantic_complete__:  # checks that all forward refs are resolved
            serializer = Serializer.parse_core_schema(
                schema=cls.__pydantic_core_schema__,
                ctx=Serializer.Context(
                    model_name=cls.__name__,
                    namespaced_attrs=cls.__xml_ns_attrs__,
                    search_mode=cls.__xml_search_mode__,
                    entity_info=XmlEntityInfo(
                        EntityLocation.ELEMENT,
                        path=cls.__xml_tag__,
                        ns=cls.__xml_ns__,
                        nsmap=cls.__xml_nsmap__,
                    ),
                ),
            )
            assert isinstance(serializer, BaseModelSerializer), "unexpected serializer type"
            cls.__xml_serializer__ = serializer
        else:
            cls.__xml_serializer__ = None

    @classmethod
    def model_rebuild(cls, **kwargs: Any) -> None:
        super().model_rebuild(**kwargs)

        if cls.__xml_serializer__ is None and cls.__pydantic_complete__:
            cls.__build_serializer__()

    @classmethod
    def from_xml_tree(cls: Type[ModelT], root: etree.Element, context: Optional[Dict[str, Any]] = None) -> ModelT:
        """
        Deserializes an xml element tree to an object of `cls` type.

        :param root: xml element to deserialize the object from
        :param context: pydantic validation context
        :return: deserialized object
        """

        assert cls.__xml_serializer__ is not None, f"model {cls.__name__} is partially initialized"

        if root.tag == cls.__xml_serializer__.element_name:
            obj = typing.cast(
                ModelT, cls.__xml_serializer__.deserialize(
                    XmlElement.from_native(root),
                    context=context,
                    sourcemap={},
                    loc=(),
                ),
            )
            return obj
        else:
            raise errors.ParsingError(
                f"root element not found (actual: {root.tag}, expected: {cls.__xml_serializer__.element_name})",
            )

    @classmethod
    def from_xml(
            cls: Type[ModelT], source: Union[str, bytes], context: Optional[Dict[str, Any]] = None, **kwargs: Any,
    ) -> ModelT:
        """
        Deserializes an xml string to an object of `cls` type.

        :param source: xml string
        :param context: pydantic validation context
        :param kwargs: additional xml deserialization arguments
        :return: deserialized object
        """

        return cls.from_xml_tree(etree.fromstring(source, **kwargs), context=context)

    def to_xml_tree(
            self, *, skip_empty: bool = False, exclude_none: bool = False, exclude_unset: bool = False,
    ) -> etree.Element:
        """
        Serializes the object to an xml tree.

        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text, Nones)
        :param exclude_none: exclude `None` values
        :param exclude_unset: exclude values that haven't been explicitly set
        :return: object xml representation
        """

        assert self.__xml_serializer__ is not None, f"model {type(self).__name__} is partially initialized"

        root = XmlElement(tag=self.__xml_serializer__.element_name, nsmap=self.__xml_serializer__.nsmap)
        self.__xml_serializer__.serialize(
            root, self, pdc.to_jsonable_python(
                self,
                by_alias=False,
                fallback=lambda obj: obj if not isinstance(obj, ElementT) else None,  # for raw fields support
            ),
            skip_empty=skip_empty,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
        )

        return root.to_native()

    def to_xml(
            self, *, skip_empty: bool = False, exclude_none: bool = False, exclude_unset: bool = False, **kwargs: Any,
    ) -> Union[str, bytes]:
        """
        Serializes the object to an xml string.

        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text, Nones)
        :param exclude_none: exclude `None` values
        :param exclude_unset: exclude values that haven't been explicitly set
        :param kwargs: additional xml serialization arguments
        :return: object xml representation
        """

        return etree.tostring(
            self.to_xml_tree(skip_empty=skip_empty, exclude_none=exclude_none, exclude_unset=exclude_unset),
            **kwargs,
        )


@te.dataclass_transform(kw_only_default=True, field_specifiers=(attr, element, wrapped, pd.Field))
class RootXmlModelMeta(XmlModelMeta, RootModelMetaclass):
    pass


RootModelRootType = TypeVar('RootModelRootType')


class RootXmlModel(
    RootModel[RootModelRootType],
    BaseXmlModel,
    Generic[RootModelRootType],
    metaclass=RootXmlModelMeta,
    __xml_abstract__=True,
):
    """
    Base pydantic-xml root model.
    """

    @classmethod
    def __build_serializer__(cls) -> None:
        if cls is RootXmlModel:
            return

        super().__build_serializer__()
