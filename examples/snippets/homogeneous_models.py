from typing import List, Literal, Optional, Tuple

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class Social(BaseXmlModel):
    type: str = attr()
    url: str


class Product(BaseXmlModel):
    status: Literal['running', 'development'] = attr()
    launched: Optional[int] = attr()
    title: str


class Company(BaseXmlModel):
    socials: Tuple[Social, ...] = element(tag='social')
    products: List[Product] = element(tag='product')
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <social type="linkedin">https://www.linkedin.com/company/spacex</social>
    <social type="twitter">https://twitter.com/spacex</social>
    <social type="youtube">https://www.youtube.com/spacex</social>

    <product status="running" launched="2013">Several launch vehicles</product>
    <product status="running" launched="2019">Starlink</product>
    <product status="development">Starship</product>
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "socials": [
        {
            "type": "linkedin",
            "url": "https://www.linkedin.com/company/spacex"
        },
        {
            "type": "twitter",
            "url": "https://twitter.com/spacex"
        },
        {
            "type": "youtube",
            "url": "https://www.youtube.com/spacex"
        }
    ],
    "products": [
        {
            "status": "running",
            "launched": 2013,
            "title": "Several launch vehicles"
        },
        {
            "status": "running",
            "launched": 2019,
            "title": "Starlink"
        },
        {
            "status": "development",
            "title": "Starship"
        }
    ]
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.parse_raw(json_doc)
