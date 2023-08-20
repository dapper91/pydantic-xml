from pydantic import constr

from pydantic_xml import BaseXmlModel


# [model-start]
class Company(BaseXmlModel):
    description: constr(strip_whitespace=True)
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    Space Exploration Technologies Corp.
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "description": "Space Exploration Technologies Corp."
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
