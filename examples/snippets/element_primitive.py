import datetime as dt

from pydantic import HttpUrl

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(BaseXmlModel, tag='company'):
    founded: dt.date = element()
    website: HttpUrl = element(tag='web-size')
# [model-end]


# [xml-start]
xml_doc = '''
<company>
    <founded>2002-03-14</founded>
    <web-size>https://www.spacex.com</web-size>
</company>
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
