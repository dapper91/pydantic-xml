import datetime as dt
import sys
from typing import Dict, Generic, List, Optional, TypeVar, Union

import pytest
from helpers import assert_xml_equal
from pydantic import ConfigDict

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, create_model, element, wrapped


def test_primitive_types():
    TestModel = create_model(
        'TestModel',
        __tag__='model',
        data=(str, ...),
        attr1=(int, attr()),
        element1=(dt.datetime, element()),
        element2=(float, wrapped('element2')),
        element3=(Optional[str], element(default=None)),
    )

    xml = '''
    <model attr1="1">text<element1>2022-07-29T23:38:17</element1><element2>2.2</element2><element3/></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        data='text',
        attr1=1,
        element1=dt.datetime(2022, 7, 29, 23, 38, 17),
        element2=2.2,
        element3=None,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_non_primitive_types():
    TestModel = create_model(
        'TestModel',
        attr1=(Union[int, str], attr()),
        element1=(Dict[str, int], element(tag='sub1')),
        element2=(List[float], wrapped('wrap', element())),
    )

    xml = '''
    <TestModel attr1="hello">
        <sub1 attr1="1" attr2="2"/>
        <wrap>
            <element2>1.1</element2>
            <element2>2.2</element2>
        </wrap>
    </TestModel>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        attr1="hello",
        element1={'attr1': 1, 'attr2': 2},
        element2=[1.1, 2.2],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model():
    TestModel = create_model(
        'TestModel',
        __tag__='model',
        __base__=RootXmlModel,
        root=(int, attr(name="attr1")),
    )

    xml = '''
    <model attr1="1"/>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_nested_model():
    TestSubModel = create_model(
        'TestSubModel',
        __tag__='sub-model',
        data=(str, ...),
    )
    TestModel = create_model(
        'TestModel',
        __tag__='model',
        sub=(TestSubModel, ...),
    )

    xml = '''
    <model>
        <sub-model>text</sub-model>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sub=TestSubModel(
            data='text',
        ),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_inheritance():
    TestBaseModel = create_model(
        'TestBaseModel',
        data=(str, ...),
    )

    TestModel = create_model(
        'TestModel',
        __base__=TestBaseModel,
        __tag__='model',
        attr1=(int, attr()),
    )

    xml = '''
    <model attr1="1">text</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        data='text',
        attr1=1,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above")
def test_annotations():
    from typing import Annotated

    TestModel = create_model(
        'TestModel',
        __tag__='model',
        attr1=Annotated[int, attr()],
        element1=Annotated[str, element()],
    )

    xml = '''
    <model attr1="1">
        <element1>text</element1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(attr1=1, element1='text')

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_generics():
    GenericType1 = TypeVar('GenericType1')
    GenericType2 = TypeVar('GenericType2')

    GenericModel = create_model(
        'GenericModel',
        __tag__='model',
        __base__=(BaseXmlModel, Generic[GenericType1, GenericType2]),
        attr1=(GenericType1, attr()),
        attr2=(GenericType2, attr()),
    )

    xml1 = '''
    <model attr1="1" attr2="2.2"/>
    '''

    TestModel = GenericModel[int, float]
    actual_obj = TestModel.from_xml(xml1)
    expected_obj = TestModel(attr1=1, attr2=2.2)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml1)

    xml2 = '''
    <model attr1="true" attr2="string"/>
    '''

    TestModel = GenericModel[bool, str]
    actual_obj = TestModel.from_xml(xml2)
    expected_obj = TestModel(attr1=True, attr2="string")

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml2)


def test_config():
    TestBaseModel1 = create_model(
        'TestBaseModel1',
        __config__=ConfigDict(str_strip_whitespace=False, str_to_lower=True),
        data=(str, ...),
    )
    TestBaseModel2 = create_model(
        'TestBaseModel2',
        __config__=ConfigDict(str_strip_whitespace=False, str_max_length=4),
        data=(str, ...),
    )

    TestModel = create_model(
        'TestModel',
        __base__=(TestBaseModel1, TestBaseModel2),
        __config__=ConfigDict(str_strip_whitespace=True),
        __tag__='model',
        data=(str, ...),
    )

    assert TestModel.model_config == ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=True,
        str_max_length=4,
    )

    xml = '''
    <model>
        TEXT
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data='text')

    assert actual_obj == expected_obj
