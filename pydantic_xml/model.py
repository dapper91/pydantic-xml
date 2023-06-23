import functools as ft
import typing
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type, TypeVar, Union

import pydantic as pd
import pydantic.fields
import pydantic.generics
import pydantic.json

from . import config, errors, serializers, utils
from .element import SearchMode
from .element.native import XmlElement, etree
from .serializers.factories import ModelSerializerFactory
from .utils import NsMap, register_nsmap


class XmlEntityInfo(pd.fields.FieldInfo):
    """
    Field xml meta-information.
    """


class XmlAttributeInfo(XmlEntityInfo):
    """
    Field xml attribute meta-information.

    :param name: attribute name
    :param ns: attribute xml namespace
    :param kwargs: pydantic field arguments. See :py:class:`pydantic.Field`
    """

    __slots__ = ('_name', '_ns')

    def __init__(
            self,
            name: Optional[str] = None,
            ns: Optional[str] = None,
            **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._name = name
        self._ns = ns

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def ns(self) -> Optional[str]:
        return self._ns


class XmlElementInfo(XmlEntityInfo):
    """
    Field xml element meta-information.

    :param tag: element tag
    :param ns: element xml namespace
    :param nsmap: element xml namespace map
    :param kwargs: pydantic field arguments
    """

    __slots__ = ('_tag', '_ns', '_nsmap')

    def __init__(
            self,
            tag: Optional[str] = None,
            ns: Optional[str] = None,
            nsmap: Optional[NsMap] = None,
            **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._tag = tag
        self._ns = ns
        self._nsmap = nsmap

        if config.REGISTER_NS_PREFIXES and nsmap:
            register_nsmap(nsmap)

    @property
    def tag(self) -> Optional[str]:
        return self._tag

    @property
    def ns(self) -> Optional[str]:
        return self._ns

    @property
    def nsmap(self) -> Optional[NsMap]:
        return self._nsmap


class XmlWrapperInfo(XmlEntityInfo):
    """
    Field xml wrapper meta-information.

    :param entity: wrapped entity
    :param path: entity path
    :param ns: element xml namespace
    :param nsmap: element xml namespace map
    :param kwargs: pydantic field arguments
    """

    __slots__ = ('_entity', '_path', '_ns', '_nsmap')

    def __init__(
            self,
            path: str,
            entity: Optional[XmlEntityInfo] = None,
            ns: Optional[str] = None,
            nsmap: Optional[NsMap] = None,
            **kwargs: Any,
    ):
        if entity is not None:
            # copy arguments from the wrapped entity to let pydantic know how to process the field
            for entity_field_name in utils.get_slots(entity):
                kwargs[entity_field_name] = getattr(entity, entity_field_name)

        super().__init__(**kwargs)
        self._entity = entity
        self._path = path
        self._ns = ns
        self._nsmap = nsmap

        if config.REGISTER_NS_PREFIXES and nsmap:
            register_nsmap(nsmap)

    @property
    def entity(self) -> Optional[XmlEntityInfo]:
        return self._entity

    @property
    def path(self) -> str:
        return self._path

    @property
    def ns(self) -> Optional[str]:
        return self._ns

    @property
    def nsmap(self) -> Optional[NsMap]:
        return self._nsmap


def attr(**kwargs: Any) -> Any:
    """
    Marks a pydantic field as an xml attribute.

    :param kwargs: see :py:class:`pydantic_xml.XmlAttributeInfo`
    """

    return XmlAttributeInfo(**kwargs)


def element(**kwargs: Any) -> Any:
    """
    Marks a pydantic field as an xml element.

    :param kwargs: see :py:class:`pydantic_xml.XmlElementInfo`
    """

    return XmlElementInfo(**kwargs)


def wrapped(*args: Any, **kwargs: Any) -> Any:
    """
    Marks a pydantic field as a wrapped xml entity.

    :param args: see :py:class:`pydantic_xml.XmlWrapperInfo`
    :param kwargs: see :py:class:`pydantic_xml.XmlWrapperInfo`
    """

    return XmlWrapperInfo(*args, **kwargs)


class XmlModelMeta(pd.main.ModelMetaclass):
    """
    Xml model metaclass.
    """

    __is_base_model_defined__ = False

    def __new__(mcls, name: str, bases: Tuple[type], namespace: Dict[str, Any], **kwargs: Any) -> Type['BaseXmlModel']:
        if mcls.__is_base_model_defined__:
            mcls._merge_configs(bases, namespace)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        if mcls.__is_base_model_defined__:
            cls.__init_serializer__()
        else:
            mcls.__is_base_model_defined__ = True

        return cls

    @classmethod
    def _merge_configs(mcls, bases: Tuple[type], namespace: Dict[str, Any]) -> None:
        xml_encoders: Dict[Type[Any], Callable[[Any], Any]] = {}
        for base in reversed(bases):
            if issubclass(base, BaseXmlModel) and base != BaseXmlModel:
                xml_encoders.update(getattr(base.__config__, 'xml_encoders', {}))

        if self_config := namespace.get('Config'):
            xml_encoders.update(getattr(self_config, 'xml_encoders', {}))
            setattr(self_config, 'xml_encoders', xml_encoders)


ModelT = TypeVar('ModelT', bound='BaseXmlModel')


class BaseXmlModel(pd.BaseModel, metaclass=XmlModelMeta):
    """
    Base pydantic-xml model.
    """

    __xml_tag__: ClassVar[Optional[str]]
    __xml_ns__: ClassVar[Optional[str]]
    __xml_nsmap__: ClassVar[Optional[NsMap]]
    __xml_ns_attrs__: ClassVar[bool]
    __xml_search_mode__: ClassVar[SearchMode]
    __xml_encoder__: ClassVar[serializers.XmlEncoder]
    __xml_serializer__: ClassVar[Optional[ModelSerializerFactory.RootSerializer]] = None

    def __init_subclass__(
            cls,
            *args: Any,
            tag: Optional[str] = None,
            ns: Optional[str] = None,
            nsmap: Optional[NsMap] = None,
            ns_attrs: Optional[bool] = None,
            search_mode: Optional[SearchMode] = None,
            **kwargs: Any,
    ):
        """
        Initializes a subclass.

        :param tag: element tag
        :param ns: element namespace
        :param nsmap: element namespace map
        :param ns_attrs: use namespaced attributes
        :param search_mode: element search mode
        """

        super().__init_subclass__(*args, **kwargs)

        cls.__xml_tag__ = tag if tag is not None else getattr(cls, '__xml_tag__', None)
        cls.__xml_ns__ = ns if ns is not None else getattr(cls, '__xml_ns__', None)
        cls.__xml_nsmap__ = nsmap if nsmap is not None else getattr(cls, '__xml_nsmap__', None)
        cls.__xml_ns_attrs__ = ns_attrs if ns_attrs is not None else getattr(cls, '__xml_ns_attrs__', False)
        cls.__xml_search_mode__ = search_mode if search_mode is not None \
            else getattr(cls, '__xml_search_mode__', SearchMode.STRICT)

        default_xml_encoder: Callable[[Any], Any]
        if xml_encoders := getattr(cls.Config, 'xml_encoders', None):
            default_xml_encoder = ft.partial(pd.json.custom_pydantic_encoder, xml_encoders)
        else:
            default_xml_encoder = pd.json.pydantic_encoder

        cls.__xml_encoder__ = serializers.XmlEncoder(default=default_xml_encoder)

    @classmethod
    def __init_serializer__(cls) -> None:
        if config.REGISTER_NS_PREFIXES and cls.__xml_nsmap__:
            register_nsmap(cls.__xml_nsmap__)

        cls.__xml_serializer__ = ModelSerializerFactory.build_root(cls)

    @classmethod
    def update_forward_refs(cls, **kwargs: Any) -> None:
        super().update_forward_refs(**kwargs)

        if cls.__xml_serializer__ is not None:
            cls.__xml_serializer__.resolve_forward_refs()

    @classmethod
    def from_xml_tree(cls: Type[ModelT], root: etree.Element) -> ModelT:
        """
        Deserializes an xml element tree to an object of `cls` type.

        :param root: xml element to deserialize the object from
        :return: deserialized object
        """

        assert cls.__xml_serializer__ is not None, f"model {cls.__name__} is partially initialized"

        if root.tag == cls.__xml_serializer__.element_name:
            obj = typing.cast(ModelT, cls.__xml_serializer__.deserialize(XmlElement.from_native(root)))
            return obj
        else:
            raise errors.ParsingError(
                f"root element not found (actual: {root.tag}, expected: {cls.__xml_serializer__.element_name})",
            )

    @classmethod
    def from_xml(cls: Type[ModelT], source: Union[str, bytes]) -> ModelT:
        """
        Deserializes an xml string to an object of `cls` type.

        :param source: xml string
        :return: deserialized object
        """

        return cls.from_xml_tree(etree.fromstring(source))

    def to_xml_tree(
            self,
            *,
            encoder: Optional[serializers.XmlEncoder] = None,
            skip_empty: bool = False,
    ) -> etree.Element:
        """
        Serializes the object to an xml tree.

        :param encoder: xml type encoder
        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text, Nones)
        :return: object xml representation
        """

        encoder = encoder or self.__xml_encoder__

        assert self.__xml_serializer__ is not None, f"model {type(self).__name__} is partially initialized"

        root = XmlElement(tag=self.__xml_serializer__.element_name, nsmap=self.__xml_serializer__.nsmap)
        self.__xml_serializer__.serialize(root, self, encoder=encoder, skip_empty=skip_empty)

        return root.to_native()

    def to_xml(
            self,
            *,
            encoder: Optional[serializers.XmlEncoder] = None,
            skip_empty: bool = False,
            **kwargs: Any,
    ) -> Union[str, bytes]:
        """
        Serializes the object to an xml string.

        :param encoder: xml type encoder
        :param skip_empty: skip empty elements (elements without sub-elements, attributes and text, Nones)
        :param kwargs: additional xml serialization arguments
        :return: object xml representation
        """

        return etree.tostring(self.to_xml_tree(encoder=encoder, skip_empty=skip_empty), **kwargs)


GenericModelT = TypeVar('GenericModelT', bound='BaseGenericXmlModel')


class BaseGenericXmlModel(BaseXmlModel, pd.generics.GenericModel):
    """
    Base pydantic-xml generic model.
    """

    def __class_getitem__(cls, params: Union[Type[Any], Tuple[Type[Any], ...]]) -> Type[Any]:
        model = super().__class_getitem__(params)
        model.__xml_tag__ = cls.__xml_tag__
        model.__xml_ns__ = cls.__xml_ns__
        model.__xml_nsmap__ = cls.__xml_nsmap__
        model.__xml_ns_attrs__ = cls.__xml_ns_attrs__
        model.__xml_search_mode__ = cls.__xml_search_mode__
        model.__init_serializer__()

        return model

    @classmethod
    def __init_serializer__(cls) -> None:
        # checks that the model is not generic
        if not getattr(cls, '__concrete__', True):
            cls.__xml_serializer__ = None
        else:
            super().__init_serializer__()

    @classmethod
    def from_xml_tree(cls: Type[GenericModelT], root: etree.Element) -> GenericModelT:
        """
        Deserializes an xml element tree to an object of `cls` type.

        :param root: xml element to deserialize the object from
        :return: deserialized object
        """

        if cls.__xml_serializer__ is None:
            raise errors.ModelError(f"{cls.__name__} model is generic")

        return super().from_xml_tree(root)
