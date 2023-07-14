from typing import Dict

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(BaseXmlModel):
    founder: Dict[str, str] = element(tag='Founder')
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <Founder name="Elon" surname="Musk"/>
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "founder": {
        "name": "Elon",
        "surname": "Musk"
    }
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
