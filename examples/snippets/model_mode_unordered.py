from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(
    BaseXmlModel,
    tag='Company',
    search_mode='unordered',
):
    founded: str = element(tag='Founded')
    website: str = element(tag='WebSite')
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <WebSite>https://www.spacex.com</WebSite>
    <Founded>2002-03-14</Founded>
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "founded": "2002-03-14",
    "website": "https://www.spacex.com"
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
