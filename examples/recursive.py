from typing import List, Optional

import pydantic_xml as pxml

xml = '''
<Directory Name="root" Mode="rwxr-xr-x">
    <Directory Name="etc" Mode="rwxr-xr-x">
        <File Name="passwd" Mode="-rw-r--r--"/>
        <File Name="hosts" Mode="-rw-r--r--"/>
        <Directory Name="ssh" Mode="rwxr-xr-x"/>
    </Directory>
    <Directory Name="bin" Mode="rwxr-xr-x"/>
    <Directory Name="usr" Mode="rwxr-xr-x">
        <Directory Name="bin" Mode="rwxr-xr-x"/>
    </Directory>
</Directory>
'''


class File(pxml.BaseXmlModel, tag="File"):
    name: str = pxml.attr(name='Name')
    mode: str = pxml.attr(name='Mode')


class Directory(pxml.BaseXmlModel, tag="Directory"):
    name: str = pxml.attr(name='Name')
    mode: str = pxml.attr(name='Mode')
    dirs: Optional[List['Directory']] = pxml.element(tag='Directory')
    files: Optional[List[File]] = pxml.element(tag='File', default_factory=list)


root = Directory.from_xml(xml)
print(root.json(indent=4))
