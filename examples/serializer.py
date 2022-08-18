import base64
from typing import Any, List

from pydantic_xml import BaseXmlModel, XmlEncoder, attr, element


class CustomXmlEncoder(XmlEncoder):
    def encode(self, obj: Any) -> str:
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode()

        return super().encode(obj)


class File(BaseXmlModel):
    name: str = attr()
    content: bytes = element()


class Files(BaseXmlModel, tag='files'):
    __root__: List[File] = element(tag='file', default=[])


files = Files()
for filename in ['file1.txt', 'file2.txt']:
    with open(filename, 'rb') as f:
        content = f.read()

    files.__root__.append(File(name=filename, content=content))

xml = files.to_xml(encoder=CustomXmlEncoder(), pretty_print=True, encoding='UTF-8', standalone=True)
print(xml.decode())
