import abc
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, Sequence, TypeVar

from pydantic_xml.typedefs import NsMap


class XmlElementReader(abc.ABC):
    """
    Xml element data reader.
    Provides an interface for extracting element text, attributes and sub-elements.
    """

    @abc.abstractmethod
    def is_empty(self) -> bool:
        """
        Checks if the element is empty (has not text, attributes or sub-elements).

        :return: `True` if the element is empty otherwise `False`.
        """

    @abc.abstractmethod
    def pop_text(self) -> Optional[str]:
        """
        Extracts the text from the xml element.
        All subsequent calls return `None`.

        :return: element text
        """

    @abc.abstractmethod
    def pop_attrib(self, name: str) -> Optional[str]:
        """
        Extracts an attribute from the xml element matching `name`.
        All subsequent calls with the same name return `None`.

        :return: element attribute
        """

    @abc.abstractmethod
    def pop_attributes(self) -> Optional[Dict[str, str]]:
        """
        Extracts all attribute from the xml element.
        All subsequent calls return `None`.

        :return: element attributes
        """

    @abc.abstractmethod
    def pop_element(self, tag: str, search_mode: 'SearchMode') -> Optional['XmlElement[Any]']:
        """
        Extracts a sub-element from the xml element matching `tag`.

        :param tag: element tag
        :param search_mode: element search mode
        :return: sub-element
        """

    @abc.abstractmethod
    def find_sub_element(self, path: Sequence[str], search_mode: 'SearchMode') -> Optional['XmlElement[Any]']:
        """
        Searches for an element at the provided path. If the element is not found returns `None`.

        :param path: path the element is searched at
        :param search_mode: element search mode
        :return: found element or `None`
        """

    @abc.abstractmethod
    def create_snapshot(self) -> 'XmlElement[Any]':
        """
        Creates a snapshot of the element. The snapshot can be modified not affecting the original one.

        :return: created snapshot
        """

    @abc.abstractmethod
    def apply_snapshot(self, snapshot: 'XmlElement[Any]') -> None:
        """
        Applies a snapshot to the current element.
        """


class XmlElementWriter(abc.ABC):
    """
    Xml element data writer.
    Provides an interface for setting element text, attributes and sub-elements.
    """

    @abc.abstractmethod
    def is_empty(self) -> bool:
        """
        Checks if the element is empty (has not text, attributes or sub-elements).

        :return: `True` if the element is empty otherwise `False`.
        """

    @abc.abstractmethod
    def set_text(self, text: str) -> None:
        """
        Sets xml element text.

        :param text: element text
        """

    @abc.abstractmethod
    def set_attribute(self, name: str, value: str) -> None:
        """
        Sets xml element attribute.

        :param name: attribute name
        :param value: attribute value
        """

    @abc.abstractmethod
    def set_attributes(self, attributes: Dict[str, str]) -> None:
        """
        Sets xml element attributes.

        :param attributes: element attributes
        """

    @abc.abstractmethod
    def append_element(self, element: 'XmlElement[Any]') -> None:
        """
        Appends a new sub-element to the xml element.

        :param element: sub-element to be added
        """

    @abc.abstractmethod
    def make_element(self, tag: str, nsmap: Optional[NsMap]) -> 'XmlElement[Any]':
        """
        Creates an element of the current element type.

        :param tag: element tag
        :param nsmap: element namespace map
        :return: created element
        """

    @abc.abstractmethod
    def find_element_or_create(self, tag: str, search_mode: 'SearchMode', nsmap: Optional[NsMap]) -> 'XmlElement[Any]':
        """
        Searches for an element with the provided tag.
        If the element is found returns it otherwise creates a new one.

        :param tag: element tag to be found or created
        :param search_mode: element search mode
        :param nsmap: element namespace mapping
        :return: xml element
        """


NativeElement = TypeVar('NativeElement')


class XmlElement(XmlElementReader, XmlElementWriter, Generic[NativeElement]):
    """
    Xml element.
    """

    NativeElementInner = TypeVar('NativeElementInner')

    class State(Generic[NativeElementInner]):
        __slots__ = ('text', 'attrib', 'elements', 'next_element_idx')

        def __init__(
                self,
                text: Optional[str],
                attrib: Optional[Dict[str, str]],
                elements: List['XmlElement[XmlElement.NativeElementInner]'],
                next_element_idx: int,
        ):
            self.text = text
            self.attrib = attrib
            self.elements = elements
            self.next_element_idx = next_element_idx

    __slots__ = ('_tag', '_nsmap')

    @classmethod
    @abc.abstractmethod
    def from_native(cls, element: NativeElement) -> 'XmlElement[NativeElement]':
        """
        Creates a instance of `XmlElement` from native element.

        :param element: native element
        :return: `XmlElement`
        """

    @abc.abstractmethod
    def to_native(self) -> NativeElement:
        """
        Transforms current element to a native one.

        :return: native element
        """

    def __init__(
            self,
            tag: str,
            text: Optional[str] = None,
            attributes: Optional[Dict[str, str]] = None,
            elements: Optional[List['XmlElement[NativeElement]']] = None,
            nsmap: Optional[NsMap] = None,
    ):
        self._tag = tag
        self._nsmap = nsmap
        self._state = XmlElement.State(
            text=text,
            attrib=dict(attributes) if attributes is not None else None,
            elements=elements or [],
            next_element_idx=0,
        )

    @property
    def tag(self) -> str:
        return self._tag

    def create_snapshot(self) -> 'XmlElement[NativeElement]':
        element = self.__class__(
            tag=self._tag,
            text=self._state.text,
            attributes=dict(self._state.attrib) if self._state.attrib is not None else None,
            elements=[element.create_snapshot() for element in self._state.elements],
            nsmap=dict(self._nsmap) if self._nsmap is not None else None,
        )
        element._state.next_element_idx = self._state.next_element_idx

        return element

    def apply_snapshot(self, snapshot: 'XmlElement[NativeElement]') -> None:
        self._tag = snapshot._tag
        self._nsmap = snapshot._nsmap
        self._state.text = snapshot._state.text
        self._state.attrib = snapshot._state.attrib
        self._state.elements = snapshot._state.elements
        self._state.next_element_idx = snapshot._state.next_element_idx

    def is_empty(self) -> bool:
        if not self._state.text and not self._state.attrib and len(self._state.elements) == 0:
            return True
        else:
            return False

    def set_text(self, text: str) -> None:
        self._state.text = text

    def set_attribute(self, name: str, value: str) -> None:
        if self._state.attrib is None:
            self._state.attrib = {}

        self._state.attrib[name] = value

    def set_attributes(self, attributes: Dict[str, str]) -> None:
        self._state.attrib = dict(attributes)

    def append_element(self, element: 'XmlElement[NativeElement]') -> None:
        self._state.elements.append(element)
        self._state.next_element_idx += 1

    def pop_text(self) -> Optional[str]:
        result, self._state.text = self._state.text, None

        return result

    def pop_attrib(self, name: str) -> Optional[str]:
        return self._state.attrib.pop(name, None) if self._state.attrib else None

    def pop_attributes(self) -> Optional[Dict[str, str]]:
        result, self._state.attrib = self._state.attrib, None

        return result

    def pop_element(self, tag: str, search_mode: 'SearchMode') -> Optional['XmlElement[NativeElement]']:
        searcher = get_searcher(search_mode)

        return searcher(self._state, tag, False)

    def find_sub_element(self, path: Sequence[str], search_mode: 'SearchMode') -> Optional['XmlElement[NativeElement]']:
        assert len(path) > 0, "path can't be empty"

        root, path = path[0], path[1:]
        element = self._find_element(root, search_mode)
        if element and path:
            return element.find_sub_element(path, search_mode)

        return element

    def find_element_or_create(
            self,
            tag: str,
            search_mode: 'SearchMode',
            nsmap: Optional[NsMap],
    ) -> 'XmlElement[NativeElement]':
        if (sub_element := self._find_element(tag, search_mode)) is None:
            sub_element = self.make_element(tag=tag, nsmap=nsmap)
            self._state.elements.append(sub_element)
            self._state.next_element_idx += 1

        return sub_element

    def _find_element(self, tag: str, search_mode: 'SearchMode') -> Optional['XmlElement[NativeElement]']:
        searcher = get_searcher(search_mode)

        return searcher(self._state, tag, True)


class SearchMode(str, Enum):
    """
    Element search mode.

    strict: search for an element sequentially one by one.
    ordered: search for an element sequentially skipping unmatched ones.
    unordered: search for an element ignoring elements order.
    """

    STRICT = 'strict'
    ORDERED = 'ordered'
    UNORDERED = 'unordered'


Searcher = Callable[[XmlElement.State[Any], str, bool], Optional[XmlElement]]


def get_searcher(search_mode: SearchMode) -> Searcher:
    if search_mode == SearchMode.STRICT:
        return strict_search
    elif search_mode == SearchMode.ORDERED:
        return ordered_search
    elif search_mode == SearchMode.UNORDERED:
        return unordered_search
    else:
        raise AssertionError('unreachable')


def strict_search(state: XmlElement.State[Any], tag: str, look_behind: bool = False) -> Optional[XmlElement[Any]]:
    """
    Searches for a sub-element sequentially one by one.

    :param state: element state
    :param tag: sub-element tag for be searched for
    :param look_behind: look for a previous element
    :return: found element or `None` if the element not found
    """

    result: Optional[XmlElement[Any]] = None

    if look_behind and (result := _look_behind(state, tag)) is not None:
        return result

    if state.next_element_idx < len(state.elements) and state.elements[state.next_element_idx].tag == tag:
        result = state.elements[state.next_element_idx]
        state.next_element_idx += 1

    return result


def ordered_search(state: XmlElement.State[Any], tag: str, look_behind: bool = False) -> Optional[XmlElement[Any]]:
    """
    Searches for an element sequentially skipping unmatched ones.

    :param state: element state
    :param tag: sub-element tag for be searched for
    :param look_behind: look for a previous element
    :return: found element or `None` if the element not found
    """

    result: Optional[XmlElement[Any]] = None

    if look_behind and (result := _look_behind(state, tag)) is not None:
        return result

    next_element_idx = state.next_element_idx
    while next_element_idx < len(state.elements):
        element = state.elements[next_element_idx]
        next_element_idx += 1

        if element.tag == tag:
            state.next_element_idx = next_element_idx
            result = element
            break

    return result


def unordered_search(
        state: XmlElement.State[Any],
        tag: str,
        look_behind: bool = False,
) -> Optional[XmlElement[Any]]:
    """
    Searches search for an element ignoring elements order.

    :param state: element state
    :param tag: sub-element tag for be searched for
    :param look_behind: look for a previous element
    :return: found element or `None` if the requested element not found
    """

    result: Optional[XmlElement[Any]] = None

    if look_behind and (result := _look_behind(state, tag)) is not None:
        return result

    for idx in range(state.next_element_idx, len(state.elements)):
        element = state.elements[idx]
        if element.tag == tag:
            state.elements[state.next_element_idx], state.elements[idx] = \
                state.elements[idx], state.elements[state.next_element_idx]
            state.next_element_idx += 1
            result = element
            break

    return result


def _look_behind(state: XmlElement.State[Any], tag: str) -> Optional[XmlElement[Any]]:
    if state.next_element_idx != 0:
        candidate = state.elements[state.next_element_idx - 1]
        if candidate.tag == tag:
            return candidate

    return None
