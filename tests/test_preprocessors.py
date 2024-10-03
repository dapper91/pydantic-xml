from typing import Any, Dict, List

import pydantic as pd
import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, xml_field_serializer, xml_field_validator
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


def test_pydantic_model_validator():
    class TestModel(BaseXmlModel, tag='model1'):
        text: str
        attr1: str = attr()
        attr2: str = attr()

        @pd.model_validator(mode='before')
        def validate_before_attr1(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            if values.get('attr1') != "expected attr value":
                raise ValueError('attr1')

            return values

        @pd.model_validator(mode='before')
        def validate_before_attr2(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            if values.get('attr2') != "expected attr value":
                raise ValueError('attr2')

            return values

        @pd.model_validator(mode='after')
        def validate_model(self) -> 'TestModel':
            if self.text != "expected text value":
                raise ValueError('text')

            return self

    xml = '<model1 attr1="expected attr value" attr2="expected attr value">expected text value</model1>'
    TestModel.from_xml(xml)

    xml = '<model1 attr1="unexpected attr value" attr2="expected attr value">expected text value</model1>'
    with pytest.raises(ValueError) as err:
        TestModel.from_xml(xml)
    assert err.value.errors()[0]['ctx']['orig'] == 'Value error, attr1'

    xml = '<model1 attr1="expected attr value" attr2="unexpected attr value">expected text value</model1>'
    with pytest.raises(ValueError) as err:
        TestModel.from_xml(xml)
    assert err.value.errors()[0]['ctx']['orig'] == 'Value error, attr2'

    xml = '<model1 attr1="expected attr value" attr2="expected attr value">unexpected text value</model1>'
    with pytest.raises(ValueError) as err:
        TestModel.from_xml(xml)
    assert err.value.errors()[0]['ctx']['orig'] == 'Value error, text'
