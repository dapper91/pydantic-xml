from typing import Literal, Optional, Tuple
from xml.etree.ElementTree import canonicalize

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class Product(BaseXmlModel, tag='Product', skip_empty=True):
    status: Optional[Literal['running', 'development']] = attr(default=None)
    launched: Optional[int] = attr(default=None)
    title: Optional[str] = element(tag='Title', default=None)


class Company(BaseXmlModel, tag='Company'):
    trade_name: str = attr(name='trade-name')
    website: str = element(tag='WebSite', default='')

    products: Tuple[Product, ...] = element()


company = Company(
    trade_name="SpaceX",
    products=[
        Product(status="running", launched=2013, title="Several launch vehicles"),
        Product(status="running", title="Starlink"),
        Product(status="development"),
        Product(),
    ],
)
# [model-end]


# [xml-start]
xml_doc = '''
<Company trade-name="SpaceX">
    <WebSite /><!--Company empty elements are not excluded-->

    <!--Product empty sub-elements and attributes are excluded-->
    <Product status="running" launched="2013">
        <Title>Several launch vehicles</Title>
    </Product>
    <Product status="running">
        <Title>Starlink</Title>
    </Product>
    <Product status="development"/>
    <Product />
</Company>
'''  # [xml-end]

assert canonicalize(company.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)
