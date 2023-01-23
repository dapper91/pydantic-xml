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


def test_root_model():
    class TestModel(BaseXmlModel, tag='model'):
        pass

    xml = '''<model1/>'''

    assert TestModel.from_xml(xml) is None


def test_skip_empty():
    class TestSubModel(BaseXmlModel, tag='model'):
        text: Optional[str]
        element1: Optional[str] = element()
        attr1: Optional[str] = attr()

    class TestModel(BaseXmlModel, tag='model'):
        model: TestSubModel
        list: List[TestSubModel] = element(default=[])
        tuple: Optional[Tuple[TestSubModel, TestSubModel]] = None
        attrs: Dict[str, str] = {}
        wrapped: Optional[str] = wrapped('envelope')

    xml = '''
    <model/>
    '''

    obj = TestModel(model=TestSubModel())

    actual_xml = obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_recursive_models():
    class TestModel(BaseXmlModel, tag='model'):
        attr1: int = attr()
        element1: float = element()

        model1: Optional['TestModel'] = element(tag='model1')
        models: Optional[List['TestModel']] = element(tag='item')

    xml = '''
        <model attr1="1">
            <element1>1.1</element1>
            <model1 attr1="2">
                <element1>2.2</element1>
            </model1>

            <item attr1="3">
                <element1>3.3</element1>
            </item>
            <item attr1="4">
                <element1>4.4</element1>
            </item>
        </model>
    '''

    obj = TestModel(
        attr1=1,
        element1=1.1,
        model1=TestModel(
            attr1=2,
            element1=2.2,
        ),
        models=[
            TestModel(
                attr1=3,
                element1=3.3,
            ),
            TestModel(
                attr1=4,
                element1=4.4,
            ),
        ],
    )

    actual_xml = obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_defaults():
    class TestModel(BaseXmlModel, tag='model'):
        attr1: int = attr(default=1)
        element1: int = element(default=1)
        text: str = 'text'
        attrs: Dict[str, str] = element(tag='model2', default={'key': 'value'})
        element2: int = wrapped('wrapper', element(tag='model3', default=2))

    xml = '<model/>'
    actual_obj: TestModel = TestModel.from_xml(xml)
    expected_obj: TestModel = TestModel()
    assert actual_obj == expected_obj

    expected_xml = '''
        <model attr1="1">text<element1>1</element1><model2 key="value"/><wrapper><model3>2</model3></wrapper></model>
    '''
    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, expected_xml.encode())


def test_default_factory():
    class TestModel(BaseXmlModel, tag='model'):
        attr1: int = attr(default_factory=lambda: 1)
        element1: int = element(default_factory=lambda: 1)
        text: str = 'text'
        attrs: Dict[str, str] = element(tag='model2', default_factory=lambda: {'key': 'value'})
        element2: int = wrapped('wrapper', element(tag='model3', default_factory=lambda: 2))

    xml = '<model/>'
    actual_obj: TestModel = TestModel.from_xml(xml)
    expected_obj: TestModel = TestModel()
    assert actual_obj == expected_obj

    expected_xml = '''
        <model attr1="1">text<element1>1</element1><model2 key="value"/><wrapper><model3>2</model3></wrapper></model>
    '''
    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, expected_xml.encode())
