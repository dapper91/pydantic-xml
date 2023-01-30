from typing import List

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Socials(
    BaseXmlModel,
    tag='socials',
    nsmap={'': 'http://www.company.com/soc'},
):
    urls: List[str] = element(tag='social')


class Contacts(
    BaseXmlModel,
    tag='contacts',
    nsmap={'': 'http://www.company.com/cnt'},
):
    socials: Socials = element()


class Company(
    BaseXmlModel,
    tag='company',
    nsmap={'': 'http://www.company.com/co'},
):
    contacts: Contacts = element()
# [model-end]


# [xml-start]
xml_doc = '''
<company xmlns="http://www.company.com/co">
    <contacts xmlns="http://www.company.com/cnt" >
        <socials xmlns="http://www.company.com/soc">
            <social>https://www.linkedin.com/company/spacex</social>
            <social>https://twitter.com/spacex</social>
            <social>https://www.youtube.com/spacex</social>
        </socials>
    </contacts>
</company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "contacts": {
        "socials": {
            "urls": [
                "https://www.linkedin.com/company/spacex",
                "https://twitter.com/spacex",
                "https://www.youtube.com/spacex"
            ]
        }
    }
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.parse_raw(json_doc)

print(company.to_xml().decode())
