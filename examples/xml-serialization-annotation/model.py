import pathlib
from typing import Annotated, List, Type
from xml.etree.ElementTree import canonicalize

import pydantic_xml as pxml
from pydantic_xml.element import XmlElementReader, XmlElementWriter


def validate_space_separated_list(
        cls: Type[pxml.BaseXmlModel],
        element: XmlElementReader,
        field_name: str,
) -> List[float]:
    if element := element.pop_element(field_name, search_mode=cls.__xml_search_mode__):
        return list(map(float, element.pop_text().split()))

    return []


def serialize_space_separated_list(
        model: pxml.BaseXmlModel,
        element: XmlElementWriter,
        value: List[float],
        field_name: str,
) -> None:
    sub_element = element.make_element(tag=field_name, nsmap=None)
    sub_element.set_text(' '.join(map(str, value)))

    element.append_element(sub_element)


SpaceSeparatedValueList = Annotated[
    List[float],
    pxml.XmlFieldValidator(validate_space_separated_list),
    pxml.XmlFieldSerializer(serialize_space_separated_list),
]


class Plot(pxml.BaseXmlModel):
    x: SpaceSeparatedValueList = pxml.element()
    y: SpaceSeparatedValueList = pxml.element()


xml_doc = pathlib.Path('./doc.xml').read_text()
plot = Plot.from_xml(xml_doc)

assert canonicalize(plot.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)
