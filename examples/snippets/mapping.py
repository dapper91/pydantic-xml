from typing import Dict

from pydantic_xml import BaseXmlModel


# [model-start]
class Company(BaseXmlModel):
    properties: Dict[str, str]
# [model-end]


# [xml-start]
xml_doc = '''
<Company trade-name="SpaceX" type="Private"/>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "properties": {
        "trade-name": "SpaceX",
        "type": "Private"
    }
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
