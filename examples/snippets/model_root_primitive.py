from pydantic_xml import BaseXmlModel, RootXmlModel


# [model-start]
class WebSite(RootXmlModel):
    root: str


class Company(BaseXmlModel, tag='company'):
    website: WebSite
# [model-end]


# [xml-start]
xml_doc = '''
<company>
    <website>https://www.spacex.com</website>
</company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "website": "https://www.spacex.com"
}
'''  # [json-end]

env = Company.from_xml(xml_doc)
assert env == Company.model_validate_json(json_doc)
