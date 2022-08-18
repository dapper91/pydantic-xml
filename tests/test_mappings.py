from typing import Dict, List, Mapping

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, errors


def test_attrs_mapping_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        attributes: Mapping[str, int]

    xml = '''
    <model attr1="1" attr2="2" attr3="3"/>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(attributes={'attr1': 1, 'attr2': 2, 'attr3': 3})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_element_mapping_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        element1: Mapping[str, int] = element(tag='element1')

    xml = '''
    <model>
        <element1 attr1="1" attr2="2" attr3="3"/>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(element1={'attr1': 1, 'attr2': 2, 'attr3': 3})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_attrs_mapping_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        __root__: Dict[str, int]

    xml = '''
    <model attr1="1" attr2="2" attr3="3"/>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(__root__={'attr1': 1, 'attr2': 2, 'attr3': 3})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_element_mapping_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        __root__: Dict[str, int] = element(tag='element1')

    xml = '''
    <model>
        <element1 attr1="1" attr2="2" attr3="3"/>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(__root__={'attr1': 1, 'attr2': 2, 'attr3': 3})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_mapping_definition_errors():
    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: Dict[str, int] = attr()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            element: Dict[str, List[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestSubModel(BaseXmlModel):
            attribute: int

        class TestModel(BaseXmlModel):
            element: Dict[str, TestSubModel]
