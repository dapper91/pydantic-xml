from typing import List, NamedTuple, Optional, Union

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element


def test_named_tuple_of_primitives_extraction():
    class TestTuple(NamedTuple):
        field1: int
        field2: float
        field3: str
        field4: Optional[str]

    class TestModel(BaseXmlModel, tag='model1'):
        elements: TestTuple = element(tag='element')

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


def test_named_tuple_of_mixed_types_extraction():
    class TestSubModel1(BaseXmlModel):
        attr1: int = attr()
        element1: float = element()

    class TestTuple(NamedTuple):
        field1: TestSubModel1
        field2: int

    class TestModel(BaseXmlModel, tag='model1'):
        submodels: TestTuple = element(tag='submodel')

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


def test_list_of_named_tuples_extraction():
    class TestTuple(NamedTuple):
        field1: int
        field2: Optional[float] = None

    class RootModel(BaseXmlModel, tag='model'):
        elements: List[TestTuple] = element(tag='element')

    xml = '''
    <model>
        <element>1</element>
        <element>1.1</element>
        <element>2</element>
        <element></element>
        <element>3</element>
        <element>3.3</element>
    </model>
    '''

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        elements=[
            (1, 1.1),
            (2, None),
            (3, 3.3),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_list_of_named_tuples_of_models_extraction():
    class SubModel1(RootXmlModel[str], tag='text'):
        pass

    class SubModel2(RootXmlModel[int], tag='number'):
        pass

    class TestTuple(NamedTuple):
        field1: SubModel1
        field2: Optional[SubModel2] = None

    class RootModel(BaseXmlModel, tag='model'):
        elements: List[TestTuple]

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


def test_primitive_union_named_tuple():
    class TestTuple(NamedTuple):
        field1: Union[int, float]
        field2: str
        field3: Union[int, float]

    class TestModel(BaseXmlModel, tag='model'):
        sublements: TestTuple = element(tag='model1')

    xml = '''
    <model>
        <model1>1.1</model1>
        <model1>text</model1>
        <model1>1</model1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=(float('1.1'), 'text', 1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
