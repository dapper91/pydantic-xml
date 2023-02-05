from pydantic_xml import BaseXmlModel


# [model-start]
class Company(BaseXmlModel, tag='company'):
    title: str
# [model-end]


# [xml-start]
xml_doc = '''
<company>SpaceX</company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "title": "SpaceX"
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.parse_raw(json_doc)
