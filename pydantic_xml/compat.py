"""
pydantic compatibility module.
"""

import re
from typing import Tuple

import pydantic as pd
from pydantic._internal._model_construction import ModelMetaclass  # noqa
from pydantic.root_model import _RootModelMetaclass as RootModelMetaclass  # noqa

VERSION_RE = re.compile(
    r"(?P<major>[0-9]+)?.*?\.?"
    r"(?P<minor>[0-9]+)?.*?\.?"
    r"(?P<micro>[0-9]+)?.*?",
)


def parse_version(version: str) -> Tuple[int, int, int]:
    if m := VERSION_RE.match(version):
        major = int(m.group(1) or 0)
        minor = int(m.group(2) or 0)
        micro = int(m.group(3) or 0)
        return major, minor, micro
    else:
        return 0, 0, 0


PYDANTIC_VERSION = parse_version(pd.__version__)


def merge_field_infos(*field_infos: pd.fields.FieldInfo) -> pd.fields.FieldInfo:
    if PYDANTIC_VERSION >= (2, 12, 0):
        return pd.fields.FieldInfo._construct(list(field_infos))
    else:
        return pd.fields.FieldInfo.merge_field_infos(*field_infos)
