from pydantic_xml import BaseXmlModel, element


# [model-start]
class Headquarters(
    BaseXmlModel,
    tag='headquarters',
    ns='hq',
    nsmap={'hq': 'http://www.company.com/hq'},
):
    country: str = element(ns='hq')
    state: str = element(ns='hq')
    city: str = element(ns='hq')


class Company(BaseXmlModel, tag='company'):
    headquarters: Headquarters
# [model-end]


# [xml-start]
xml_doc = '''
<company>
    <hq:headquarters xmlns:hq="http://www.company.com/hq">
        <hq:country>US</hq:country>
        <hq:state>California</hq:state>
        <hq:city>Hawthorne</hq:city>
    </hq:headquarters>
</company>

'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "headquarters": {
        "country": "US",
        "state": "California",
        "city": "Hawthorne"
    }
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
