import datetime as dt
import ipaddress
from decimal import Decimal
from enum import Enum
from typing import Any


class XmlEncoder:
    """
    Xml data encoder.
    """

    def encode(self, obj: Any) -> str:
        """
        Encodes provided object into a string

        :param obj: object to be encoded
        :return: encoded object
        """

        if isinstance(obj, str):
            return obj
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, (int, float, Decimal)):
            return str(obj)
        if isinstance(obj, (dt.datetime, dt.date, dt.time)):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return self.encode(obj.value)
        if isinstance(
            obj, (
                ipaddress.IPv4Address,
                ipaddress.IPv6Address,
                ipaddress.IPv4Network,
                ipaddress.IPv6Network,
                ipaddress.IPv4Interface,
                ipaddress.IPv6Interface,
            ),
        ):
            return str(obj)

        return self.default(obj)

    def default(self, obj: Any) -> str:
        raise TypeError(f'Object of type {obj.__class__.__name__} is not XML serializable')


DEFAULT_ENCODER = XmlEncoder()
