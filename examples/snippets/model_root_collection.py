from typing import Dict

from pydantic_xml import BaseXmlModel


# [model-start]
class Company(BaseXmlModel, tag='company'):
    __root__: Dict[str, str]
# [model-end]


# [xml-start]
xml_doc = '''
<company trade-name="SpaceX" type="Private"/>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "trade-name": "SpaceX",
    "type":"Private"
}
'''  # [json-end]

env = Company.from_xml(xml_doc)
assert env == Company.parse_raw(json_doc)
