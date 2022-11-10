from typing import Dict, List, Optional

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, wrapped


def test_wrapped_primitive_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        data: int = wrapped('model2')

    xml = '''
    <model1>
        <model2>1</model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_submodel_extraction():
    class TestSubModel(BaseXmlModel, tag='model4'):
        attr1: int = attr()

    class TestModel(BaseXmlModel, tag='model1'):
        data: TestSubModel = wrapped('model2/model3', element())
        empty: Optional[TestSubModel] = wrapped('model2/model4', element())

    xml = '''
    <model1>
        <model2>
            <model3>
                <model4 attr1="1"/>
            </model3>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=TestSubModel(attr1=1))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_mapping_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        attrs: Dict[str, str] = wrapped('model2/model3')

    xml = '''
    <model1>
        <model2>
            <model3 attr1="1" attr2="2"/>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(attrs={'attr1': 1, 'attr2': 2})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_collection_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        elements: List[int] = wrapped('model2/model3', element(tag='model4'))

    xml = '''
    <model1>
        <model2>
            <model3>
                <model4>1</model4>
                <model4>2</model4>
                <model4>3</model4>
            </model3>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=[1, 2, 3])

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
