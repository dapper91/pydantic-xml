from typing import Optional

from pydantic_xml import BaseXmlModel


# [model-start]
class Company(BaseXmlModel):
    description: Optional[str] = None
# [model-end]


# [xml-start]
xml_doc = '''
<Company></Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "description": null
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
