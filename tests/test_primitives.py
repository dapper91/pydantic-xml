import datetime as dt
from typing import Generic, Optional, TypeVar

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element


def test_text_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        data: str

    xml = '''
    <model>text</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        data='text',
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_attrs_and_elements_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        attr1: str = attr()
        attr2: int = attr()

        element1: float = element()
        element2: dt.datetime = element()

    xml = '''
    <model attr1="string1" attr2="2">
        <element1>1.1</element1>
        <element2>2022-07-29T23:38:17</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        attr1='string1',
        attr2=2,
        element1=1.1,
        element2=dt.datetime(2022, 7, 29, 23, 38, 17),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_nillable_element_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        element1: Optional[int] = element(default=None, nillable=True)
        element2: Optional[int] = element(default=None, nillable=True)
        element3: Optional[int] = element(default=None, nillable=True)

    src_xml = '''
    <model>
        <element1 xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />
        <element2 xsi:nil="false" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">2</element2>
        <element3>3</element3>
    </model>
    '''

    actual_obj = TestModel.from_xml(src_xml)
    expected_obj = TestModel(element1=None, element2=2, element3=3)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    expected_xml = '''
    <model>
        <element1 xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />
        <element2>2</element2>
        <element3>3</element3>
    </model>
    '''

    assert_xml_equal(actual_xml, expected_xml)


def test_model_inheritance():
    class TestModel4(BaseXmlModel):
        attr1: int = attr()

    class TestModel3(TestModel4):
        attr2: str = attr()
        element1: float = element()

    class TestModel2(BaseXmlModel):
        element1: str = element()

    class TestModel1(TestModel2, TestModel3, tag='model1'):
        pass

    xml = '''
    <model1 attr1="1" attr2="string2">
        <element1>text</element1>
    </model1>
    '''

    actual_obj = TestModel1.from_xml(xml)
    expected_obj = TestModel1(
        attr1=1,
        attr2="string2",
        element1="text",
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_text_extraction_syntax1():
    class TestModel(RootXmlModel, tag='model'):
        root: int

    xml = '''
    <model>1</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_text_extraction_syntax2():
    T = TypeVar('T')

    class TestRootModel(RootXmlModel[T], Generic[T], tag='model'):
        pass

    xml = '''
    <model>1</model>
    '''

    TestModel = TestRootModel[int]
    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_text_extraction_syntax3():
    class TestModel(RootXmlModel[int], tag='model'):
        pass

    xml = '''
    <model>1</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_text_extraction_syntax4():
    class TestRootModel(RootXmlModel, tag='model'):
        pass

    xml = '''
    <model>1</model>
    '''

    TestModel = TestRootModel[int]
    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_attr_extraction():
    class TestModel(RootXmlModel, tag='model'):
        root: int = attr(name="attr1")

    xml = '''
    <model attr1="1"/>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_element_extraction():
    class TestModel(RootXmlModel, tag='model'):
        root: int = element(tag="element1")

    xml = '''
    <model>
        <element1>1</element1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_nillable_element_extraction():
    class TestModel(RootXmlModel, tag='model'):
        root: Optional[int] = element(tag="element1", default=None, nillable=True)

    xml = '''
    <model>
        <element1 xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel()

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_default():
    class TestRootModel(RootXmlModel, tag='sub'):
        root: int = 1

    class TestModel(BaseXmlModel, tag='model'):
        sub: TestRootModel

    xml = '''
    <model><sub></sub></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(sub=TestRootModel(1))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()

    expected_xml = '''
    <model><sub>1</sub></model>
    '''
    assert_xml_equal(actual_xml, expected_xml)
