import dataclasses as dc
import re
from collections import ChainMap
from typing import Dict, Optional, cast

from .backend import etree

NsMap = Dict[str, str]


@dc.dataclass(frozen=True)
class QName:
    """
    XML entity qualified name.

    :param tag: entity tag
    :param ns: entity namespace
    """

    tag: str
    ns: Optional[str]

    @classmethod
    def from_uri(cls, uri: str) -> 'QName':
        """
        Creates `QName` from uri.

        :param uri: entity uri in format '{namespace}tag'
        :return: qualified name
        """

        if (m := re.match(r'({(.*)})?(.*)', uri)) is None:
            raise ValueError

        return cls(tag=m[3], ns=m[2])

    @classmethod
    def from_alias(cls, tag: str, ns: Optional[str] = None, nsmap: Optional[NsMap] = None) -> 'QName':
        """
        Creates `QName` from namespace alias.

        :param tag: entity tag
        :param ns: xml namespace alias
        :param nsmap: xml namespace mapping
        :return: qualified name
        """

        return QName(tag=tag, ns=nsmap.get(ns) if ns and nsmap else None)

    @property
    def uri(self) -> str:
        return '{%s}%s' % (self.ns, self.tag) if self.ns else self.tag

    def __str__(self) -> str:
        return self.uri


def merge_nsmaps(*maps: Optional[NsMap]) -> NsMap:
    """
    Merges multiple namespace maps into s single one respecting provided order.

    :param maps: namespace maps
    :return: merged namespace
    """

    return cast(NsMap, ChainMap(*(nsmap for nsmap in maps if nsmap)))


def register_nsmap(nsmap: NsMap) -> None:
    """
    Registers namespaces prefixes from the map.
    """

    for prefix, uri in nsmap.items():
        if prefix != '':  # skip default namespace
            etree.register_namespace(prefix, uri)
