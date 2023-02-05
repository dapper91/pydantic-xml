from typing import List, Tuple, Union

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element


def test_primitive_union():
    class TestModel(BaseXmlModel, tag='model'):
        text: Union[int, float, str]
        field1: Union[int, float, str] = element(tag='field')
        attr1: Union[int, float, str] = attr()

    xml = '''
    <model attr1="1">text<field>inf</field></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        text='text',
        field1=float('inf'),
        attr1=1,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_model_union():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        text: float

    class TestModel(BaseXmlModel, tag='model'):
        field1: Union[SubModel1, SubModel2] = element()

    xml = '''
    <model><model1 attr1="1"></model1></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel1(attr1=1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)

    xml = '''
    <model><model2>inf</model2></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel2(text=float('inf')),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_union_list():
    class TestModel(BaseXmlModel, tag='model'):
        sublements: List[Union[int, float, str]] = element(tag='model1')

    xml = '''
    <model>
        <model1>1</model1>
        <model1>inf</model1>
        <model1>text</model1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=[1, float('inf'), 'text'],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_model_union_list():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        element1: float

    class TestModel(BaseXmlModel, tag='model'):
        sublements: List[Union[SubModel1, SubModel2]] = element()

    xml = '''
    <model>
        <model1 attr1="1"/>
        <model2>inf</model2>
        <model1 attr1="2"/>
        <model2>-inf</model2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=[
            SubModel1(attr1=1),
            SubModel2(element1=float('inf')),
            SubModel1(attr1=2),
            SubModel2(element1=float('-inf')),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_union_tuple():
    class TestModel(BaseXmlModel, tag='model'):
        sublements: Tuple[Union[int, float], str, Union[int, float]] = element(tag='model1')

    xml = '''
    <model>
        <model1>inf</model1>
        <model1>text</model1>
        <model1>1</model1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=(float('inf'), 'text', 1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_definition_errors():
    with pytest.raises(TypeError):
        class SubModel(BaseXmlModel):
            pass

        class TestModel(BaseXmlModel):
            field1: Union[int, SubModel]
