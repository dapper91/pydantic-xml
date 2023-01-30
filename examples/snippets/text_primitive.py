from pydantic_xml import BaseXmlModel


# [model-start]
class Company(BaseXmlModel):
    class Config:
        anystr_strip_whitespace = True  # to strip text whitespaces

    description: str
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
assert company == Company.parse_raw(json_doc)
