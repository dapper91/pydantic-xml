from typing import Optional, Union

from lxml import etree

from pydantic_xml.element import XmlElement as BaseXmlElement
from pydantic_xml.typedefs import NsMap

__all__ = (
    'XmlElement',
    'etree',
)


class XmlElement(BaseXmlElement[etree._Element]):
    @classmethod
    def from_native(cls, element: etree._Element) -> 'XmlElement':
        return cls(
            tag=element.tag,
            text=element.text,
            attributes={
                force_str(name): force_str(value)  # str transformation safe since lxml byte values are ASCII compatible
                for name, value in element.attrib.items()
            },
            elements=[
                XmlElement.from_native(sub_element)
                for sub_element in element
                if not is_xml_comment(sub_element)
            ],
        )

    def to_native(self) -> etree._Element:
        element = etree.Element(
            self._tag,
            attrib=self._state.attrib,
            # https://github.com/lxml/lxml-stubs/issues/76
            nsmap={ns or None: uri for ns, uri in self._nsmap.items()} if self._nsmap else None,  # type: ignore[misc]
        )
        element.text = self._state.text
        element.extend([element.to_native() for element in self._state.elements])

        return element

    def make_element(self, tag: str, nsmap: Optional[NsMap]) -> 'XmlElement':
        return XmlElement(tag, nsmap=nsmap)


def force_str(val: Union[str, bytes]) -> str:
    if isinstance(val, bytes):
        return val.decode()
    else:
        return val


def is_xml_comment(element: etree._Element) -> bool:
    return isinstance(element, etree._Comment)
