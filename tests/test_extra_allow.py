from pydantic import ValidationError
from pydantic_xml import BaseXmlModel, attr, element

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
    assert "p2" == actual_obj.model_extra["prop2"]


def test_extra_elements():

    class TestModelChild(BaseXmlModel, tag="child"):
        data: str

    class TestModel(BaseXmlModel, tag='model', extra='allow'):
        child: TestModelChild

    xml = '''
    <model prop1="p1" prop2="p2">
        <child>hello world!</child>
        <extra_child>hi again...</extra_child>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    assert "hello world!" == actual_obj.child.data
    assert "extra_child" in actual_obj.model_extra


def test_extra_save():

    class TestModelChild(BaseXmlModel, tag="child"):
        data: str

    class TestModel(BaseXmlModel, tag='model', extra='allow'):
        child: TestModelChild

    xml = '''
    <model prop1="p1" prop2="p2">
        <child>hello world!</child>
        <extra_child>hi again...</extra_child>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
