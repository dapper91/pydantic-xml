import typing
import xml.etree.ElementTree as std_etree
from typing import Any, Dict, Optional

from lxml import etree

__all__ = (
    'etree',
    'create_element',
)


def create_element(
        tag: str,
        attrib: Optional[Dict[str, Any]] = None,
        nsmap: Optional[Dict[str, str]] = None,
) -> std_etree.Element:
    element = etree.Element(
        tag,
        attrib=attrib,
        # https://github.com/lxml/lxml-stubs/issues/76
        nsmap={ns or None: uri for ns, uri in nsmap.items()} if nsmap else None,  # type: ignore[misc]
    )

    return typing.cast(std_etree.Element, element)  # lxml Element copies xml.etree.Element interface
