"""
pydantic compatibility module.
"""

import pydantic as pd
from pydantic._internal._model_construction import ModelMetaclass  # noqa
from pydantic.root_model import _RootModelMetaclass as RootModelMetaclass  # noqa

PYDANTIC_VERSION = tuple(map(int, pd.__version__.partition('+')[0].split('.')))


def merge_field_infos(*field_infos: pd.fields.FieldInfo) -> pd.fields.FieldInfo:
    if PYDANTIC_VERSION >= (2, 12, 0):
        return pd.fields.FieldInfo._construct(field_infos)  # type: ignore[attr-defined]
    else:
        return pd.fields.FieldInfo.merge_field_infos(*field_infos)
