from typing import Optional

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, errors


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
        model2: Optional[TestSubModel] = None

    xml = '''<model1/>'''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model2=None)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_nillable_submodel_element_extraction():
    class TestSubModel(BaseXmlModel):
        text: int

    class TestModel(BaseXmlModel, tag='model1'):
        model2: Optional[TestSubModel] = element(default=None, nillable=True)
        model3: Optional[TestSubModel] = element(default=None, nillable=True)
        model4: Optional[TestSubModel] = element(default=None, nillable=True)

    xml = '''
    <model1>
        <model2 xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />
        <model3 xsi:nil="false" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">3</model3>
        <model4>4</model4>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model2=None,
        model3=TestSubModel(text=3),
        model4=TestSubModel(text=4),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    expected_xml = '''
    <model1>
        <model2 xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />
        <model3>3</model3>
        <model4>4</model4>
    </model1>
    '''

    assert_xml_equal(actual_xml, expected_xml)


def test_root_submodel_element_extraction():
    class TestSubModel(RootXmlModel, tag='model2'):
        root: int

    class TestModel(BaseXmlModel, tag='model1'):
        model2: TestSubModel = element()

    xml = '''
    <model1>
        <model2>1</model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model2=TestSubModel(1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_submodel_root_extraction():
    class TestSubModel(RootXmlModel, tag='model2'):
        root: int

    class TestModel(RootXmlModel, tag='model1'):
        root: TestSubModel

    xml = '''
    <model1>
        <model2>1</model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(TestSubModel(1))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_nested_root_submodel_element_extraction():
    class TestSubModel2(RootXmlModel, tag='model2'):
        root: int

    class TestSubModel1(RootXmlModel):
        root: TestSubModel2

    class TestModel(BaseXmlModel, tag='model1'):
        element1: TestSubModel1 = element()

    xml = '''
    <model1>
        <element1>
            <model2>1</model2>
        </element1>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=TestSubModel1(TestSubModel2(1)),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_definition_errors():
    class TestSubModel(BaseXmlModel):
        attribute: int

    with pytest.raises(errors.ModelFieldError):

        class TestModel(BaseXmlModel):
            attr1: TestSubModel = attr()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: TestSubModel = attr()
