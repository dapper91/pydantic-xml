import xml.etree.ElementTree as etree
from typing import Optional

from pydantic_xml.element import XmlElement as BaseXmlElement
from pydantic_xml.typedefs import NsMap

__all__ = (
    'XmlElement',
    'etree',
)


class XmlElement(BaseXmlElement[etree.Element]):
    @classmethod
    def from_native(cls, element: etree.Element) -> 'XmlElement':
        return cls(
            tag=element.tag,
            text=element.text,
            attributes=dict(element.attrib),
            elements=[
                XmlElement.from_native(sub_element)
                for sub_element in element
                if not is_xml_comment(sub_element)
            ],
        )

    def to_native(self) -> etree.Element:
        element = etree.Element(self._tag, attrib=self._state.attrib or {})
        element.text = self._state.text
        element.extend([element.to_native() for element in self._state.elements])

        return element

    def make_element(self, tag: str, nsmap: Optional[NsMap]) -> 'XmlElement':
        return XmlElement(tag)


def is_xml_comment(element: etree.Element) -> bool:
    return element.tag is etree.Comment  # type: ignore[comparison-overlap]
