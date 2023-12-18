import dataclasses as dc
import itertools as it
import re
from collections import ChainMap
from typing import Dict, Iterable, List, Mapping, Optional, Union, cast

import pydantic as pd
import pydantic_core as pdc

from .element.native import etree
from .typedefs import Location, NsMap


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


def select_ns(*nss: Optional[str]) -> Optional[str]:
    for ns in nss:
        if ns is not None:
            return ns

    return None


def build_validation_error(
        title: str,
        errors_map: Mapping[Union[None, str, int], pd.ValidationError],
) -> pd.ValidationError:
    line_errors: List[pdc.InitErrorDetails] = []
    for location, validation_error in errors_map.items():
        for error in validation_error.errors():
            line_errors.append(
                pdc.InitErrorDetails(
                    type=pdc.PydanticCustomError(error['type'], error['msg'], error.get('ctx')),
                    loc=(location, *error['loc']) if location is not None else error['loc'],
                    input=error['input'],
                ),
            )

    return pd.ValidationError.from_exception_data(
        title=title,
        input_type='json',
        line_errors=line_errors,
    )


def set_validation_error_sourceline(err: pd.ValidationError, sourcemap: Dict[Location, int]) -> pd.ValidationError:
    line_errors: List[pdc.InitErrorDetails] = []
    for error in err.errors():
        loc, sourceline = error['loc'], -1
        while loc and (sourceline := sourcemap.get(loc, sourceline)) == -1:
            loc = tuple(loc[:-1])

        line_errors.append(
            pdc.InitErrorDetails(
                type=pdc.PydanticCustomError(
                    error['type'],
                    "[line {sourceline}]: {orig}",
                    {'sourceline': sourceline, 'orig': error['msg']},
                ),
                loc=error['loc'],
                input=error['input'],
            ),
        )

    return pd.ValidationError.from_exception_data(
        err.title,
        line_errors=line_errors,
    )
