from typing import Dict, List, Optional, Tuple

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, wrapped


def test_xml_declaration():
    class TestModel(BaseXmlModel, tag='model'):
        pass

    xml = '''<?xml version="1.0" encoding="utf-8"?>
    <model/>
    '''

    actual_obj = TestModel.from_xml(xml.encode())
    expected_obj = TestModel()

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(xml_declaration=True, encoding='utf-8')
    assert_xml_equal(actual_xml, xml.encode())


def test_skip_empty():
    class TestSubModel(BaseXmlModel, tag='model'):
        text: Optional[str]
        element1: Optional[str] = element()
        attr1: Optional[str] = attr()

    class TestModel(BaseXmlModel, tag='model'):
        model: TestSubModel
        list: List[TestSubModel] = []
        tuple: Optional[Tuple[TestSubModel, TestSubModel]] = None
        attrs: Dict[str, str] = {}
        wrapped: Optional[str] = wrapped('envelope')

    xml = '''
    <model/>
    '''

    obj = TestModel(model=TestSubModel())

    actual_xml = obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml.encode())
