from unittest.mock import ANY

import pydantic

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(
    BaseXmlModel,
    tag='Company',
    search_mode='strict',
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
{}
'''  # [json-end]

try:
    Company.from_xml(xml_doc)
except pydantic.ValidationError as e:
    error = e.errors()[0]
    assert error == {
        'loc': ('founded',),
        'msg': '[line 2]: Field required',
        'ctx': {'orig': 'Field required', 'sourceline': 2},
        'type': 'missing',
        'input': ANY,
    }
else:
    raise AssertionError('exception not raised')
