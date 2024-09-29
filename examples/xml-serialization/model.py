import pathlib
from typing import List
from xml.etree.ElementTree import canonicalize

from pydantic_xml import BaseXmlModel, element, xml_field_serializer, xml_field_validator
from pydantic_xml.element import XmlElementReader, XmlElementWriter


class Plot(BaseXmlModel):
    x: List[float] = element()
    y: List[float] = element()

    @xml_field_validator('x', 'y')
    def validate_space_separated_list(cls, element: XmlElementReader, field_name: str) -> List[float]:
        if element := element.pop_element(field_name, search_mode=cls.__xml_search_mode__):
            return list(map(float, element.pop_text().split()))

        return []

    @xml_field_serializer('x', 'y')
    def serialize_space_separated_list(self, element: XmlElementWriter, value: List[float], field_name: str) -> None:
        sub_element = element.make_element(tag=field_name, nsmap=None)
        sub_element.set_text(' '.join(map(str, value)))

        element.append_element(sub_element)


xml_doc = pathlib.Path('./doc.xml').read_text()
plot = Plot.from_xml(xml_doc)

assert canonicalize(plot.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)
