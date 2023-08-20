from pydantic import HttpUrl

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class Company(BaseXmlModel, tag='company'):
    title: str = attr(alias='trade-name')
    website: HttpUrl = element(alias='web-site')
# [model-end]


# [xml-start]
xml_doc = '''
<company trade-name="SpaceX">
    <web-site>https://www.spacex.com</web-site>
</company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "trade-name": "SpaceX",
    "web-site": "https://www.spacex.com"
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
