from pydantic import ValidationError
from pydantic_xml import BaseXmlModel, attr, element
from pydantic_xml.element.native import ElementT

import pytest

from tests.helpers import assert_xml_equal


def test_extra_attributes_ignored():
    class TestModel(BaseXmlModel, tag='model', extra='ignore'):
        prop1: str = attr()
        data: str

    xml = '''
    <model prop1="p1" prop2="p2">text</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    assert actual_obj.model_extra is None


def test_extra_attributes_forbidden():
    class TestModel(BaseXmlModel, tag='model', extra='forbid'):
        prop1: str = attr()
        data: str

    xml = '''
    <model prop1="p1" prop2="p2">text</model>
    '''

    with pytest.raises(ValidationError):
        _ = TestModel.from_xml(xml)


def test_extra_attributes():
    class TestModel(BaseXmlModel, tag='model', extra='allow'):
        prop1: str = attr()
        data: str

    xml = '''
    <model prop1="p1" prop2="p2">text</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    assert 'p2' == actual_obj.model_extra['prop2']


def test_extra_elements():

    class TestModelChild(BaseXmlModel, tag='child'):
        data: str

    class TestModel(BaseXmlModel, tag='model', extra='allow'):
        child: TestModelChild

    xml = '''
    <model>
        <child>hello world!</child>
        <extra_child>hi again...</extra_child>
        <extra_nested>
            <extra_sub>1</extra_sub>
            <extra_sub>2</extra_sub>
            <extra_sub>3</extra_sub>
            <extra_subsub>
                <extra_subsubsub>3.14</extra_subsubsub>
            </extra_subsub>
        </extra_nested>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    assert 'hello world!' == actual_obj.child.data
    assert 'extra_child' in actual_obj.model_extra
    assert 'extra_nested' in actual_obj.model_extra


def test_raw_save():
    # Just for debugging!!!

    class TestModel(BaseXmlModel, tag='model', arbitrary_types_allowed=True):
        extra_nested: ElementT = element()

    xml = '''
    <model>
        <extra_nested>
            <extra_sub>1</extra_sub>
            <extra_sub>2</extra_sub>
            <extra_sub>3</extra_sub>
            <extra_subsub subprop="x">
                <extra_subsubsub>3.14</extra_subsubsub>
            </extra_subsub>
        </extra_nested>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_extra_save():

    class TestModelChild(BaseXmlModel, tag='child'):
        data: str

    class TestModel(BaseXmlModel, tag='model', extra='allow'):
        prop1: str = attr()
        child: TestModelChild

    xml = '''
    <model prop1="p1" prop2="p2" prop3="p3">
        <child>hello world!</child>
        <extra_child>hi again...</extra_child>
        <extra_nested>
            <extra_sub>1</extra_sub>
            <extra_sub>2</extra_sub>
            <extra_sub>3</extra_sub>
            <extra_subsub subprop="x">
                <extra_subsubsub>3.14</extra_subsubsub>
            </extra_subsub>
        </extra_nested>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
