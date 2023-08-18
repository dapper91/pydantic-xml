from typing import Annotated, Optional, TypeVar
from xml.etree.ElementTree import canonicalize

from pydantic import BeforeValidator, PlainSerializer

from pydantic_xml import BaseXmlModel, element

InnerType = TypeVar('InnerType')
XmlOptional = Annotated[
    Optional[InnerType],
    PlainSerializer(lambda val: val if val is not None else 'null'),
    BeforeValidator(lambda val: val if val != 'null' else None),
]


class Company(BaseXmlModel):
    title: XmlOptional[str] = element(default=None)


xml_doc = '''
<Company>
    <title>null</title>
</Company>
'''

company = Company.from_xml(xml_doc)

assert company.title is None
assert canonicalize(company.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)
