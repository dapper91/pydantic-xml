import base64
import pathlib
from typing import List, Optional, Union
from xml.etree.ElementTree import canonicalize

from pydantic import field_serializer, field_validator

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element


class File(BaseXmlModel):
    name: str = attr()
    content: bytes = element()

    @field_serializer('content')
    def encode_content(self, value: bytes) -> str:
        return base64.b64encode(value).decode()

    @field_validator('content', mode='before')
    def decode_content(cls, value: Optional[Union[str, bytes]]) -> Optional[bytes]:
        if isinstance(value, str):
            return base64.b64decode(value)

        return value


class Files(RootXmlModel, tag='files'):
    root: List[File] = element(tag='file', default=[])


files = Files()
for filename in ['./file1.txt', './file2.txt']:
    with open(filename, 'rb') as f:
        content = f.read()

    files.root.append(File(name=filename, content=content))

expected_xml_doc = pathlib.Path('./doc.xml').read_bytes()

assert canonicalize(files.to_xml(), strip_text=True) == canonicalize(expected_xml_doc, strip_text=True)
