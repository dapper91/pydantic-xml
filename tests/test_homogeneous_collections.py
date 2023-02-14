from typing import Dict, List, Set, Tuple

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, errors


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
    class SubModel(BaseXmlModel):
        __root__: int

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
            SubModel(__root__=1),
            SubModel(__root__=2),
            SubModel(__root__=3),
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


def test_text_list_extraction():
    class RootModel(BaseXmlModel, tag="model"):
        values: List[int]

    xml = '''
    <model>1 2 70 -34</model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        values = [1, 2, 70, -34],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_homogeneous_definition_errors():
    breakpoint()
    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: List[Tuple[int, ...]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            attr1: List[Tuple[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            __root__: List[int]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            __root__: List[List[int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            __root__: List[Tuple[int, ...]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            __root__: List[Dict[int, int]]

    with pytest.raises(errors.ModelFieldError):
        class TestSubModel(BaseXmlModel):
            attr: int

        class TestModel(BaseXmlModel):
            __root__: List[TestSubModel]
