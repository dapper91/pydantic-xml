from typing import Dict

from pydantic_xml import RootXmlModel


# [model-start]
class Company(RootXmlModel, tag='company'):
    root: Dict[str, str]
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
assert env == Company.model_validate_json(json_doc)
