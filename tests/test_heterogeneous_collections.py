from typing import Dict, List, Optional, Tuple

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, errors


def test_set_of_primitives_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        elements: Tuple[int, float, str, Optional[str]] = element(tag='element')

    xml = '''
    <model1>
        <element>1</element>
        <element>2.2</element>
        <element>string3</element>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=(1, 2.2, "string3", None))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml)


def test_tuple_of_nillable_primitives_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        elements: Tuple[Optional[int], Optional[float], Optional[str]] = element(tag='element', nillable=True)

    xml = '''
    <model1>
        <element>1</element>
        <element xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />
        <element>string3</element>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=(1, None, "string3"))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_tuple_of_submodel_extraction():
    class TestSubModel1(BaseXmlModel):
        attr1: int = attr()
        element1: float = element()

    class TestModel(BaseXmlModel, tag='model1'):
        submodels: Tuple[TestSubModel1, int] = element(tag='submodel')

    xml = '''
    <model1>
        <submodel attr1="1">
            <element1>2.2</element1>
        </submodel>
        <submodel>1</submodel>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        submodels=[
            TestSubModel1(attr1=1, element1=2.2),
            1,
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_root_submodel_extraction():
    class TestSubModel1(RootXmlModel):
        root: int

    class TestModel(BaseXmlModel, tag='model1'):
        elements: Tuple[float, TestSubModel1] = element(tag='element')

    xml = '''
    <model1>
        <element>1.1</element>
        <element>2</element>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        elements=[
            1.1,
            TestSubModel1(2),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_dict_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        elements: Tuple[int, Dict[str, int]] = element(tag='element')

    xml = '''
    <model1>
        <element>1</element>
        <element attr1="1" attr2="2"/>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        elements=[
            1,
            {'attr1': 1, 'attr2': 2},
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_tuple_of_submodels_extraction():
    class TestSubModel(BaseXmlModel, tag='model2'):
        text: int

    class TestModel(RootXmlModel, tag='model1'):
        root: Tuple[TestSubModel, TestSubModel, TestSubModel]

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


def test_heterogeneous_collection_definition_errors():
    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: Tuple[int, int] = attr()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: Tuple[List[int], List[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: Tuple[Tuple[int], Tuple[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: Tuple[List[int], int]

    with pytest.raises(errors.ModelFieldError):
        class TestSubModel(RootXmlModel):
            root: int

        class TestModel(RootXmlModel):
            root: Tuple[TestSubModel, int]
