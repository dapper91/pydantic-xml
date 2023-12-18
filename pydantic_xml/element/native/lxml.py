import typing
from typing import Optional, Union

from lxml import etree

from pydantic_xml.element import XmlElement as BaseXmlElement
from pydantic_xml.typedefs import NsMap

__all__ = (
    'ElementT',
    'XmlElement',
    'etree',
)

ElementT = etree._Element


class XmlElement(BaseXmlElement[ElementT]):
    @classmethod
    def from_native(cls, element: ElementT) -> 'XmlElement':
        return cls(
            tag=element.tag,
            text=element.text,
            tail=element.tail,
            attributes={
                force_str(name): force_str(value)  # transformation is safe since lxml bytes values are ASCII compatible
                for name, value in element.attrib.items()
            },
            elements=[
                XmlElement.from_native(sub_element)
                for sub_element in element
                if not is_xml_comment(sub_element)
            ],
            sourceline=typing.cast(int, element.sourceline) if element.sourceline is not None else -1,
        )

    def to_native(self) -> ElementT:
        element = etree.Element(
            self._tag,
            attrib=self._state.attrib,
            # https://github.com/lxml/lxml-stubs/issues/76
            nsmap={ns or None: uri for ns, uri in self._nsmap.items()} if self._nsmap else None,  # type: ignore[misc]
        )
        element.text = self._state.text
        element.tail = self._state.tail
        element.extend([element.to_native() for element in self._state.elements])

        return element

    def make_element(self, tag: str, nsmap: Optional[NsMap]) -> 'XmlElement':
        return XmlElement(tag, nsmap=nsmap)

    def get_sourceline(self) -> int:
        return self._sourceline


def force_str(val: Union[str, bytes]) -> str:
    if isinstance(val, bytes):
        return val.decode()
    else:
        return val


def is_xml_comment(element: ElementT) -> bool:
    return isinstance(element, etree._Comment)
