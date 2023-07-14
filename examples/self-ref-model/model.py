import pathlib
from typing import List, Optional

from pydantic_xml import BaseXmlModel, attr, element


class File(BaseXmlModel, tag="File"):
    name: str = attr(name='Name')
    mode: str = attr(name='Mode')


class Directory(BaseXmlModel, tag="Directory"):
    name: str = attr(name='Name')
    mode: str = attr(name='Mode')
    dirs: Optional[List['Directory']] = element(tag='Directory', default=None)
    files: Optional[List[File]] = element(tag='File', default_factory=list)


xml_doc = pathlib.Path('./doc.xml').read_text()

directory = Directory.from_xml(xml_doc)

json_doc = pathlib.Path('./doc.json').read_text()
assert directory == Directory.model_validate_json(json_doc)
