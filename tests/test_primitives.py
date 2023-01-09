import datetime as dt
import ipaddress

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element


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
        element3: ipaddress.IPv4Address = element()

    xml = '''
    <model attr1="string1" attr2="2">
        <element1>1.1</element1>
        <element2>2022-07-29T23:38:17</element2>
        <element3>10.0.1.212</element3>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        attr1='string1',
        attr2=2,
        element1=1.1,
        element2=dt.datetime(2022, 7, 29, 23, 38, 17),
        element3=ipaddress.IPv4Address("10.0.1.212")
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


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


def test_root_model_text_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        __root__: int

    xml = '''
    <model>1</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(__root__=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_attr_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        __root__: int = attr(name="attr1")

    xml = '''
    <model attr1="1"/>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(__root__=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_element_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        __root__: int = element(tag="element1")

    xml = '''
    <model>
        <element1>1</element1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(__root__=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
