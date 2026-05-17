from typing import Annotated, Optional
from xml.etree.ElementTree import canonicalize

from pydantic_xml import BaseXmlModel, NoXml, element


class Company(BaseXmlModel):
    title: str = element()
    website: Annotated[Optional[str], NoXml] = element(default=None)


xml_doc = '''
<Company>
    <title>SpaceX</title>
</Company>
'''

company = Company.from_xml(xml_doc)

assert canonicalize(company.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)

json_doc = '''
{
    "title": "SpaceX",
    "website": "https://spacex.com/"
}
'''
company = Company.model_validate_json(json_doc)
assert company.model_dump_json(indent=4) == json_doc.strip()
