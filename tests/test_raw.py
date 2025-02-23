from typing import List, Optional, Tuple

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, element, wrapped
from pydantic_xml.element.native import ElementT, etree


def test_raw_primitive_element_serialization():
    class TestModel(BaseXmlModel, tag='model', arbitrary_types_allowed=True, extra='forbid'):
        element1: ElementT = element()
        element2: ElementT = element()

    xml = '''
    <model>
        <element1 attr1="1">text</element1>
        <element2><sub-element1 />tail</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    assert actual_obj.element1.tag == 'element1'
    assert actual_obj.element1.attrib == {'attr1': '1'}
    assert actual_obj.element1.text == 'text'

    sub_elements = list(actual_obj.element2)
    assert len(sub_elements) == 1
    assert sub_elements[0].tag == 'sub-element1'
    assert sub_elements[0].tail == 'tail'

    element1 = etree.Element('element1', attr1='1')
    element1.text = 'text'

    element2 = etree.Element('element2')
    sub_element = etree.Element('sub-element1')
    sub_element.tail = 'tail'
    element2.append(sub_element)

    actual_obj = TestModel(element1=element1, element2=element2)
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_optional_raw_primitive_element_serialization():
    class TestModel(BaseXmlModel, tag='model', arbitrary_types_allowed=True, extra='forbid'):
        element1: Optional[ElementT] = element(default=None)
        element2: ElementT = element()

    xml = '''
    <model>
        <element2>text</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    assert actual_obj.element1 is None
    assert actual_obj.element2.text == 'text'

    element2 = etree.Element('element2')
    element2.text = 'text'
    actual_obj = TestModel(element1=None, element2=element2)
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_raw_element_homogeneous_collection_serialization():
    class TestModel(BaseXmlModel, tag='model', arbitrary_types_allowed=True, extra='forbid'):
        field1: List[ElementT] = element(tag="element1")

    xml = '''
    <model>
        <element1 attr1="1">text 1</element1>
        <element1>text 2</element1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    assert len(actual_obj.field1) == 2
    assert actual_obj.field1[0].tag == 'element1'
    assert actual_obj.field1[0].attrib == {'attr1': '1'}
    assert actual_obj.field1[0].text == 'text 1'
    assert actual_obj.field1[1].tag == 'element1'
    assert actual_obj.field1[1].text == 'text 2'

    field10 = etree.Element('element1', attr1='1')
    field10.text = 'text 1'

    field11 = etree.Element('element1')
    field11.text = 'text 2'

    actual_obj = TestModel(field1=[field10, field11])
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_raw_element_heterogeneous_collection_serialization():
    class TestModel(BaseXmlModel, tag='model', arbitrary_types_allowed=True, extra='forbid'):
        field1: Tuple[ElementT, ElementT] = element(tag="element1")

    xml = '''
    <model>
        <element1 attr1="1">text 1</element1>
        <element1>text 2</element1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    assert len(actual_obj.field1) == 2
    assert actual_obj.field1[0].tag == 'element1'
    assert actual_obj.field1[0].attrib == {'attr1': '1'}
    assert actual_obj.field1[0].text == 'text 1'
    assert actual_obj.field1[1].tag == 'element1'
    assert actual_obj.field1[1].text == 'text 2'

    field10 = etree.Element('element1', attr1='1')
    field10.text = 'text 1'

    field11 = etree.Element('element1')
    field11.text = 'text 2'

    actual_obj = TestModel(field1=[field10, field11])
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_raw_element_serialization():
    class TestModel(BaseXmlModel, tag='model', arbitrary_types_allowed=True, extra='forbid'):
        field1: ElementT = wrapped('wrapper', element(tag="element1"))

    xml = '''
    <model>
        <wrapper>
            <element1 attr1="1">text 1</element1>
        </wrapper>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    assert actual_obj.field1.tag == 'element1'
    assert actual_obj.field1.attrib == {'attr1': '1'}
    assert actual_obj.field1.text == 'text 1'

    field1 = etree.Element('element1', attr1='1')
    field1.text = 'text 1'

    actual_obj = TestModel(field1=field1)
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
