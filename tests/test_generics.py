from typing import Generic, TypeVar

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseGenericXmlModel, BaseXmlModel, attr, errors


def test_root_generic_model():
    GenericType1 = TypeVar('GenericType1')
    GenericType2 = TypeVar('GenericType2')

    class GenericModel(BaseGenericXmlModel, Generic[GenericType1, GenericType2], tag='model1'):
        attr1: GenericType1 = attr()
        attr2: GenericType2 = attr()

    xml1 = '''
    <model1 attr1="1" attr2="2.2"/>
    '''

    TestModel = GenericModel[int, float]
    actual_obj = TestModel.from_xml(xml1)
    expected_obj = TestModel(attr1=1, attr2=2.2)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml1)

    xml2 = '''
    <model1 attr1="true" attr2="string"/>
    '''

    TestModel = GenericModel[bool, str]
    actual_obj = TestModel.from_xml(xml2)
    expected_obj = TestModel(attr1=True, attr2="string")

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml2)


def test_generic_submodel():
    GenericType = TypeVar('GenericType')

    class GenericSubModel(BaseGenericXmlModel, Generic[GenericType]):
        attr1: GenericType = attr()

    class TestModel(BaseXmlModel, tag='model1'):
        model2: GenericSubModel[int]
        model3: GenericSubModel[float]

    xml = '''
    <model1>
        <model2 attr1="1"/>
        <model3 attr1="1.1"/>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model2=GenericSubModel[int](attr1=1),
        model3=GenericSubModel[float](attr1=1.1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_generic_model_errors():
    GenericType = TypeVar('GenericType')

    with pytest.raises(errors.ModelError):
        class GenericModel(BaseGenericXmlModel, Generic[GenericType], tag='model1'):
            attr1: GenericType = attr()

        GenericModel.from_xml('<model1/>')
