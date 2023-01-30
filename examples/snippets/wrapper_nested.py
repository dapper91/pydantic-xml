from pydantic_xml import BaseXmlModel, element, wrapped


# [model-start]
class Company(
    BaseXmlModel,
    ns='co',
    nsmap={'co': 'http://company.org/co'},
):
    class Config:
        anystr_strip_whitespace = True  # to strip text whitespaces

    city: str = wrapped(
        'Info',
        ns='co',
        entity=wrapped(
            'Headquarters/Location',
            ns='hq',
            nsmap={'hq': 'http://company.org/hq'},
            entity=element(
                tag='City',
                ns='loc',
                nsmap={'loc': 'http://company.org/loc'},
            ),
        ),
    )
# [model-end]


# [xml-start]
xml_doc = '''
<co:Company xmlns:co="http://company.org/co">
    <co:Info>
        <hq:Headquarters xmlns:hq="http://company.org/hq">
            <hq:Location>
                <loc:City xmlns:loc="http://company.org/loc">
                    Hawthorne
                </loc:City>
            </hq:Location>
        </hq:Headquarters>
    </co:Info>
</co:Company>
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
