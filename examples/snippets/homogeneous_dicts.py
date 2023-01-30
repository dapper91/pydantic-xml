from typing import Dict, List

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(BaseXmlModel):
    products: List[Dict[str, str]] = element(tag='product')
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <product status="running" launched="2013"/>
    <product status="running" launched="2019"/>
    <product status="development"/>
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "products": [
        {
            "status": "running",
            "launched": 2013
        },
        {
            "status": "running",
            "launched": 2019
        },
        {
            "status": "development"
        }
    ]
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.parse_raw(json_doc)
