from pydantic_xml import BaseXmlModel, element


# [model-start]
class Headquarters(BaseXmlModel, tag='headquarters'):
    country: str = element()
    state: str = element()
    city: str = element()


class Company(BaseXmlModel, tag='company'):
    headquarters: Headquarters
# [model-end]


# [xml-start]
xml_doc = '''
<company>
    <headquarters>
        <country>US</country>
        <state>California</state>
        <city>Hawthorne</city>
    </headquarters>
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
