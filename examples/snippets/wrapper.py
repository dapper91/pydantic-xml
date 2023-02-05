from pydantic_xml import BaseXmlModel, element, wrapped


# [model-start]
class Company(BaseXmlModel):
    city: str = wrapped(
        'Info/Headquarters/Location',
        element(tag='City'),
    )
    country: str = wrapped(
        'Info/Headquarters/Location/Country',
    )
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <Info>
        <Headquarters>
            <Location>
                <City>Hawthorne</City>
                <Country>US</Country>
            </Location>
        </Headquarters>
    </Info>
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "country": "US",
    "city": "Hawthorne"
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.parse_raw(json_doc)
