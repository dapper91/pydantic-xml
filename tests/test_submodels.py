from typing import Optional

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, errors


def test_submodel_element_extraction():
    class TestSubModel(BaseXmlModel, tag='model2'):
        attr1: int = attr()
        element1: float = element()

    class TestModel(BaseXmlModel, tag='model1'):
        model2: TestSubModel

    xml = '''
    <model1>
        <model2 attr1="1">
            <element1>2.2</element1>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model2=TestSubModel(
            attr1=1,
            element1=2.2,
        ),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_optional_submodel_element_extraction():
    class TestSubModel(BaseXmlModel, tag='model2'):
        element1: float = element()

    class TestModel(BaseXmlModel, tag='model1'):
        model2: Optional[TestSubModel]

    xml = '''<model1/>'''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model2=None)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_submodel_element_extraction():
    class TestSubModel(BaseXmlModel, tag='model2'):
        __root__: int

    class TestModel(BaseXmlModel, tag='model1'):
        model2: TestSubModel = element()

    xml = '''
    <model1>
        <model2>1</model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model2=TestSubModel(__root__=1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_submodel_root_extraction():
    class TestSubModel(BaseXmlModel, tag='model2'):
        __root__: int

    class TestModel(BaseXmlModel, tag='model1'):
        __root__: TestSubModel

    xml = '''
    <model1>
        <model2>1</model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        __root__=TestSubModel(__root__=1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_nested_root_submodel_element_extraction():
    class TestSubModel2(BaseXmlModel, tag='model3'):
        __root__: int

    class TestSubModel1(BaseXmlModel):
        __root__: TestSubModel2

    class TestModel(BaseXmlModel, tag='model1'):
        element1: TestSubModel1 = element()

    xml = '''
    <model1>
        <element1>
            <model3>1</model3>
        </element1>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=TestSubModel1(__root__=TestSubModel2(__root__=1)),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_definition_errors():
    with pytest.raises(errors.ModelFieldError):
        class TestSubModel(BaseXmlModel):
            attribute: int

        class TestModel(BaseXmlModel):
            attr1: TestSubModel = attr()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(BaseXmlModel):
            __root__: TestSubModel = attr()
