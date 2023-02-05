import pathlib
from datetime import date
from enum import Enum
from typing import Dict, List, Literal, Optional, Set, Tuple

import pydantic as pd
from pydantic import HttpUrl, conint

from pydantic_xml import BaseXmlModel, attr, element, wrapped

NSMAP = {
    'co': 'http://www.company.com/contact',
    'hq': 'http://www.company.com/hq',
    'pd': 'http://www.company.com/prod',
}


class Headquarters(BaseXmlModel, ns='hq', nsmap=NSMAP):
    country: str = element()
    state: str = element()
    city: str = element()

    @pd.validator('country')
    def validate_country(cls, value: str) -> str:
        if len(value) > 2:
            raise ValueError('country must be of 2 characters')
        return value


class Industries(BaseXmlModel):
    __root__: Set[str] = element(tag='Industry')


class Social(BaseXmlModel, ns_attrs=True, ns='co', nsmap=NSMAP):
    type: str = attr()
    url: HttpUrl


class Product(BaseXmlModel, ns_attrs=True, ns='pd', nsmap=NSMAP):
    status: Literal['running', 'development'] = attr()
    launched: Optional[int] = attr()
    title: str


class Person(BaseXmlModel):
    name: str = attr()


class CEO(Person):
    position: Literal['CEO'] = attr()


class CTO(Person):
    position: Literal['CTO'] = attr()


class COO(Person):
    position: Literal['COO'] = attr()


class Company(BaseXmlModel, tag='Company', nsmap=NSMAP):
    class CompanyType(str, Enum):
        PRIVATE = 'Private'
        PUBLIC = 'Public'

    trade_name: str = attr(name='trade-name')
    type: CompanyType = attr()
    founder: Dict[str, str] = element(tag='Founder')
    founded: Optional[date] = element(tag='Founded')
    employees: conint(gt=0) = element(tag='Employees')
    website: HttpUrl = element(tag='WebSite')

    industries: Industries = element(tag='Industries')

    key_people: Tuple[CEO, CTO, COO] = wrapped('key-people', element(tag='person'))
    headquarters: Headquarters
    socials: List[Social] = wrapped(
        'contacts/socials',
        element(tag='social', default_factory=list),
        ns='co',
        nsmap=NSMAP,
    )

    products: Tuple[Product, ...] = element(tag='product', ns='pd')


xml_doc = pathlib.Path('./doc.xml').read_text()

company = Company.from_xml(xml_doc)

assert company == Company.parse_file('./doc.json')
