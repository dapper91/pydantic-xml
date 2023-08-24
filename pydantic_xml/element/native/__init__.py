from typing import Any, Type

from pydantic_xml import config
from pydantic_xml.element import XmlElement as BaseXmlElement

XmlElement: Type[BaseXmlElement[Any]]
ElementT: Type[Any]

if config.FORCE_STD_XML:
    from .std import *  # noqa: F403
else:
    try:
        from .lxml import *  # type: ignore[no-redef]  # noqa: F403
    except ImportError:
        from .std import *  # noqa: F403
