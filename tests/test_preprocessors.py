from typing import List

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, element, xml_field_serializer, xml_field_validator
from pydantic_xml.element import XmlElementReader, XmlElementWriter


def test_xml_field_validator():
    class TestModel(BaseXmlModel, tag='model1'):
        element1: List[int] = element()

        @xml_field_validator('element1')
        def validate_element(cls, element: XmlElementReader, field_name: str) -> List[int]:
            if element := element.pop_element(field_name, search_mode=cls.__xml_search_mode__):
                return list(map(int, element.pop_text().split()))

            return []

    xml = '''
    <model1>
        <element1>1 2 3 4 5</element1>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=[1, 2, 3, 4, 5],
    )

    assert actual_obj == expected_obj


def test_xml_field_serializer():
    class TestModel(BaseXmlModel, tag='model1'):
        element1: List[int] = element()

        @xml_field_serializer('element1')
        def serialize_element(self, element: XmlElementWriter, value: List[int], field_name: str) -> None:
            sub_element = element.make_element(tag=field_name, nsmap=None)
            sub_element.set_text(' '.join(map(str, value)))

            element.append_element(sub_element)

    expected_xml = '''
    <model1>
        <element1>1 2 3 4 5</element1>
    </model1>
    '''

    obj = TestModel(
        element1=[1, 2, 3, 4, 5],
    )

    actual_xml = obj.to_xml()
    assert_xml_equal(actual_xml, expected_xml)
