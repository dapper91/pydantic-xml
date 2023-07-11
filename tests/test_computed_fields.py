from helpers import assert_xml_equal
from pydantic import computed_field

from pydantic_xml import BaseXmlModel, computed_attr, computed_element


def test_computed_field():
    class TestModel(BaseXmlModel, tag='model'):
        @computed_field
        def element1(self) -> str:
            return 'text'

    xml = '''
    <model>text</model>
    '''

    actual_obj = TestModel.from_xml(xml)

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_computed_attributes():
    class TestModel(BaseXmlModel, tag='model'):
        @computed_attr(name='attr1')
        def computed_attr1(self) -> str:
            return 'string1'

        @computed_attr
        def attr2(self) -> str:
            return 'string2'

    xml = '''
    <model attr1="string1" attr2="string2" />
    '''

    actual_obj = TestModel.from_xml(xml)

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_computed_elements():
    class TestModel(BaseXmlModel, tag='model'):
        @computed_element(tag='element1')
        def computed_element1(self) -> str:
            return 'text1'

        @computed_element
        def element2(self) -> str:
            return 'text2'

    xml = '''
    <model>
        <element1>text1</element1>
        <element2>text2</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_computed_submodel():
    class TestSumModel(BaseXmlModel):
        text: str

    class TestModel(BaseXmlModel, tag='model'):
        @computed_field(alias='submodel1')
        def computed_submodel1(self) -> TestSumModel:
            return TestSumModel(text='text1')

        @computed_element(tag='submodel2')
        def submodel2(self) -> TestSumModel:
            return TestSumModel(text='text2')

    xml = '''
    <model>
        <submodel1>text1</submodel1>
        <submodel2>text2</submodel2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
