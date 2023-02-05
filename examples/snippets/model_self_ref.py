from typing import List, Optional

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class Directory(BaseXmlModel, tag="Directory"):
    name: str = attr(name='Name')
    dirs: Optional[List['Directory']] = element(tag='Directory')
# [model-end]


# [xml-start]
xml_doc = '''
<Directory Name="root">
    <Directory Name="etc">
        <Directory Name="ssh"/>
        <Directory Name="init"/>
    </Directory>
    <Directory Name="bin"/>
</Directory>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "name": "root",
    "dirs": [
        {
            "name": "etc",
            "dirs": [
                {
                    "name": "ssh"
                },
                {
                    "name": "init"
                }
            ]
        },
        {
            "name": "bin"
        }
    ]
}
'''  # [json-end]

directory = Directory.from_xml(xml_doc)
assert directory == Directory.parse_raw(json_doc)
