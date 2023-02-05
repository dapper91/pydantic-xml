from typing import Any, Callable, Optional, Set


class XmlEncoder:
    """
    Xml data encoder.
    """

    def __init__(self, default: Optional[Callable[[Any], Any]] = None):
        self._default = default

    def encode(self, obj: Any) -> str:
        """
        Encodes provided object into a string

        :param obj: object to be encoded
        :return: encoded object
        """

        return self._encode(obj, set())

    def _encode(self, obj: Any, seen_values: Set[int]) -> str:
        if isinstance(obj, str):
            return obj
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, int):
            # int.__repr__ is used to correctly encode int-derived types, for example enum.IntEnum
            return str(int.__repr__(obj))
        if isinstance(obj, float):
            return str(obj)

        value = self.default(obj)

        value_id = id(value)
        if value_id in seen_values:
            raise ValueError("Circular reference detected")
        else:
            seen_values.add(value_id)
            return self._encode(value, seen_values)

    def default(self, obj: Any) -> Any:
        if self._default is not None:
            try:
                return self._default(obj)
            except TypeError:
                pass

        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not XML serializable")


DEFAULT_ENCODER = XmlEncoder()
