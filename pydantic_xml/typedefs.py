from enum import IntEnum
from typing import Dict, Tuple, Union

Location = Tuple[Union[str, int], ...]
NsMap = Dict[str, str]


class EntityLocation(IntEnum):
    """
    Field data location.
    """

    ELEMENT = 1  # entity data is located at xml element
    ATTRIBUTE = 2  # entity data is located at xml attribute
    WRAPPED = 3  # entity data is wrapped by an element
