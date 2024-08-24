from typing import Literal, Optional
from xml.etree.ElementTree import canonicalize

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Product(BaseXmlModel, tag='Product'):
    title: Optional[str] = element(tag='Title', default=None)
    status: Optional[Literal['running', 'development']] = element(tag='Status', default=None)
    launched: Optional[int] = element(tag='Launched', default=None)


product = Product(title="Starlink", status=None)
xml = product.to_xml(exclude_unset=True)
# [model-end]


# [xml-start]
xml_doc = '''
<Product>
    <Title>Starlink</Title>
    <Status />
</Product>
'''  # [xml-end]

assert canonicalize(xml, strip_text=True) == canonicalize(xml_doc, strip_text=True)
