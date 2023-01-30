import base64
import pathlib
from typing import List, Optional, Union
from xml.etree.ElementTree import canonicalize

import pydantic

from pydantic_xml import BaseXmlModel, attr, element


class File(BaseXmlModel):
    name: str = attr()
    content: bytes = element()

    @pydantic.validator('content', pre=True)
    def decode_content(cls, value: Optional[Union[str, bytes]]) -> Optional[bytes]:
        if isinstance(value, str):
            return base64.b64decode(value)

        return value


class Files(BaseXmlModel, tag='files'):
    class Config:
        xml_encoders = {
            bytes: lambda value: base64.b64encode(value).decode(),
        }

    __root__: List[File] = element(tag='file', default=[])


files = Files()
for filename in ['./file1.txt', './file2.txt']:
    with open(filename, 'rb') as f:
        content = f.read()

    files.__root__.append(File(name=filename, content=content))

expected_xml_doc = pathlib.Path('./doc.xml').read_bytes()

assert canonicalize(files.to_xml(), strip_text=True) == canonicalize(expected_xml_doc, strip_text=True)
