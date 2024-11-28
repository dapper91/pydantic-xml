import datetime as dt

from pydantic import HttpUrl

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(
    BaseXmlModel,
    tag='company',
    ns='co',
    nsmap={'co': 'http://www.company.com/co'},
):
    founded: dt.date = element()
    website: HttpUrl = element(tag='web-site', ns='co')
# [model-end]


# [xml-start]
xml_doc = '''
<co:company xmlns:co="http://www.company.com/co">
    <co:founded>2002-03-14</co:founded>
    <co:web-site>https://www.spacex.com</co:web-site>
</co:company>
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
