from typing import Optional
from xml.etree.ElementTree import canonicalize

from pydantic_xml import BaseXmlModel, element


class Company(BaseXmlModel):
    title: Optional[str] = element(default=None, nillable=True)


xml_doc = '''
<Company>
    <title xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />
</Company>
'''

company = Company.from_xml(xml_doc)

assert company.title is None
assert canonicalize(company.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)
