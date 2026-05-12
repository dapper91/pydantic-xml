"""
pydantic compatibility module.
"""

import pydantic as pd
from packaging.version import Version
from pydantic._internal._model_construction import ModelMetaclass  # noqa
from pydantic.root_model import _RootModelMetaclass as RootModelMetaclass  # noqa

PYDANTIC_VERSION = Version(pd.__version__)


def merge_field_infos(*field_infos: pd.fields.FieldInfo) -> pd.fields.FieldInfo:
    if PYDANTIC_VERSION >= Version('2.12.0'):
        return pd.fields.FieldInfo._construct(list(field_infos))
    else:
        return pd.fields.FieldInfo.merge_field_infos(*field_infos)
