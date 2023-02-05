from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(BaseXmlModel, tag='Company', search_mode='ordered'):
    founded: str = element(tag='Founded')
    website: str = element(tag='WebSite')
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <Founded>2002-03-14</Founded>
    <Founder name="Elon" surname="Musk"/>
    <WebSite>https://www.spacex.com</WebSite>
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
assert company == Company.parse_raw(json_doc)
