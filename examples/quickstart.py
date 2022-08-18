from datetime import date
from enum import Enum
from typing import Dict, List, Literal, Optional, Set, Tuple

import pydantic as pd
from pydantic import HttpUrl, conint

from pydantic_xml import BaseXmlModel, attr, element, wrapped

document = '''
<Company trade-name="SpaceX" type="Private" xmlns:pd="http://www.test.com/prod">
    <Founder name="Elon" surname="Musk"/>
    <Founded>2002-03-14</Founded>
    <Employees>12000</Employees>
    <WebSite>https://www.spacex.com</WebSite>

    <Industries>
        <Industry>space</Industry>
        <Industry>communications</Industry>
    </Industries>

    <key-people>
        <person position="CEO" name="Elon Musk"/>
        <person position="CTO" name="Elon Musk"/>
        <person position="COO" name="Gwynne Shotwell"/>
    </key-people>

    <hq:headquarters xmlns:hq="http://www.test.com/hq">
        <hq:country>US</hq:country>
        <hq:state>California</hq:state>
        <hq:city>Hawthorne</hq:city>
    </hq:headquarters>

    <co:contacts xmlns:co="http://www.test.com/contact" >
        <co:socials>
            <co:social co:type="linkedin">https://www.linkedin.com/company/spacex</co:social>
            <co:social co:type="twitter">https://twitter.com/spacex</co:social>
            <co:social co:type="youtube">https://www.youtube.com/spacex</co:social>
        </co:socials>
    </co:contacts>

    <pd:product pd:status="running" pd:launched="2013">Several launch vehicles</pd:product>
    <pd:product pd:status="running" pd:launched="2019">Starlink</pd:product>
    <pd:product pd:status="development">Starship</pd:product>
</Company>
'''


class Headquarters(BaseXmlModel, ns='hq', nsmap={'hq': 'http://www.test.com/hq'}):
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


class Social(BaseXmlModel, ns_attrs=True, inherit_ns=True):
    type: str = attr()
    url: str


class Product(BaseXmlModel, ns_attrs=True, inherit_ns=True):
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


class Company(BaseXmlModel, tag='Company', nsmap={'pd': 'http://www.test.com/prod'}):
    class CompanyType(str, Enum):
        PRIVATE = 'Private'
        PUBLIC = 'Public'

    trade_name: str = attr(name='trade-name')
    type: CompanyType = attr()
    employees: conint(gt=0) = element(tag='Employees')
    website: HttpUrl = element(tag='WebSite')

    founder: Dict[str, str] = element(tag='Founder')
    founded: Optional[date] = element(tag='Founded')
    industries: Industries = element(tag='Industries')

    key_people: Tuple[CEO, CTO, COO] = wrapped('key-people', element(tag='person'))
    headquarters: Headquarters
    socials: List[Social] = wrapped(
        'contacts/socials',
        element(tag='social', default_factory=list),
        ns='co',
        nsmap={'co': 'http://www.test.com/contact'},
    )

    products: Tuple[Product, ...] = element(tag='product', ns='pd')


company = Company.from_xml(document)

print(company.json(indent=4))
