import dataclasses as dc
import itertools as it
import re
from collections import ChainMap
from typing import Iterable, Optional, cast

from .element.native import etree
from .typedefs import NsMap


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
    def from_alias(
            cls, tag: str, ns: Optional[str] = None, nsmap: Optional[NsMap] = None, is_attr: bool = False,
    ) -> 'QName':
        """
        Creates `QName` from namespace alias.

        :param tag: entity tag
        :param ns: xml namespace alias
        :param nsmap: xml namespace mapping
        :param is_attr: is the tag of attribute type
        :return: qualified name
        """

        if not is_attr or ns is not None:
            ns = nsmap.get(ns or '') if nsmap else None

        return QName(tag=tag, ns=ns)

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


def get_slots(o: object) -> Iterable[str]:
    return it.chain.from_iterable(getattr(cls, '__slots__', []) for cls in o.__class__.__mro__)
