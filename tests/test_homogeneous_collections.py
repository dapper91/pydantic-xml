from typing import Dict, List, Optional, Set, Tuple

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, errors


def test_set_of_primitives_extraction():
    class RootModel(BaseXmlModel, tag='model'):
        elements: Set[int] = element(tag='element')

    xml = '''
    <model>
        <element>1</element>
        <element>2</element>
        <element>3</element>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(elements={1, 2, 3})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_tuple_of_submodels_extraction():
    class SubModel1(BaseXmlModel):
        attr1: int = attr()
        element1: float = element()

    class RootModel(BaseXmlModel, tag='model'):
        submodels: Tuple[SubModel1, ...] = element(tag='submodel')

    xml = '''
    <model>
        <submodel attr1="1">
            <element1>2.2</element1>
        </submodel>
        <submodel attr1="2">
            <element1>4.4</element1>
        </submodel>
        <submodel attr1="3">
            <element1>6.6</element1>
        </submodel>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        submodels=[
            SubModel1(attr1=1, element1=2.2),
            SubModel1(attr1=2, element1=4.4),
            SubModel1(attr1=3, element1=6.6),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_root_submodels_extraction():
    class SubModel(RootXmlModel):
        root: int

    class RootModel(BaseXmlModel, tag='model'):
        elements: List[SubModel] = element(tag='element')

    xml = '''
    <model>
        <element>1</element>
        <element>2</element>
        <element>3</element>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        elements=[
            SubModel(1),
            SubModel(2),
            SubModel(3),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_dicts_extraction():
    class RootModel(BaseXmlModel, tag='model'):
        elements: List[Dict[str, int]] = element(tag='element')

    xml = '''
    <model>
        <element attr1="1" attr2="2"/>
        <element attr3="3"/>
        <element/>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        elements=[
            {'attr1': 1, 'attr2': 2},
            {'attr3': 3},
            {},
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_tuples_extraction():
    class RootModel(BaseXmlModel, tag='model'):
        elements: List[Tuple[str, Optional[int]]] = element(tag='element')

    xml = '''
    <model>
        <element>text1</element>
        <element>1</element>
        <element>text2</element>
        <element></element>
        <element>text3</element>
        <element>3</element>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        elements=[
            ('text1', 1),
            ('text2', None),
            ('text3', 3),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_tuples_of_models_extraction():
    class SubModel1(RootXmlModel[str], tag='text'):
        pass

    class SubModel2(RootXmlModel[int], tag='number'):
        pass

    class RootModel(BaseXmlModel, tag='model'):
        elements: List[Tuple[SubModel1, Optional[SubModel2]]]

    xml = '''
    <model>
        <text>text1</text>
        <number>1</number>
        <text>text2</text>
        <text>text3</text>
        <number>3</number>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        elements=[
            (SubModel1('text1'), SubModel2(1)),
            (SubModel1('text2'), None),
            (SubModel1('text3'), SubModel2(3)),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_list_of_submodels_extraction():
    class TestSubModel(BaseXmlModel, tag='model2'):
        text: int

    class TestModel(RootXmlModel, tag='model1'):
        root: List[TestSubModel] = element()

    xml = '''
    <model1>
        <model2>1</model2>
        <model2>2</model2>
        <model2>3</model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        [
            TestSubModel(text=1),
            TestSubModel(text=2),
            TestSubModel(text=3),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_homogeneous_collection_definition_errors():
    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: List[int] = attr()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: List[Tuple[int, ...]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: List[Tuple[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: List[List[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: List[Tuple[int, ...]]
