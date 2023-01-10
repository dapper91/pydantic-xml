import xml.etree.ElementTree as etree
from typing import Any, Dict, Optional

__all__ = (
    'etree',
    'create_element',
)


def create_element(
        tag: str,
        attrib: Optional[Dict[str, Any]] = None,
        nsmap: Optional[Dict[str, str]] = None,  # not supported by `xml.etree`
) -> etree.Element:
    return etree.Element(tag, attrib=attrib or {})
