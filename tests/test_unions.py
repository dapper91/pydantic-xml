import sys
from typing import List, Literal, Tuple, Union

import pytest
from helpers import assert_xml_equal
from pydantic import Field

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element


def test_primitive_union():
    class TestModel(BaseXmlModel, tag='model'):
        text: Union[int, float, str]
        field1: Union[int, float] = element(tag='field')
        attr1: Union[int, float] = attr()

    xml = '''
    <model attr1="1">text<field>inf</field></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        text='text',
        field1=float('inf'),
        attr1=1,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_model_union():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        text: float

    class TestModel(BaseXmlModel, tag='model'):
        field1: Union[SubModel1, SubModel2] = element()

    xml = '''
    <model><model1 attr1="1"></model1></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel1(attr1=1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)

    xml = '''
    <model><model2>inf</model2></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel2(text=float('inf')),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_similar_model_union():
    class SubModel1(BaseXmlModel, tag='model1'):
        text: float

    class SubModel2(BaseXmlModel, tag='model2'):
        text: float

    class TestModel(BaseXmlModel, tag='model'):
        field1: Union[SubModel1, SubModel2] = element()

    xml = '''
    <model><model1>0.0</model1></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel1(text=0.0),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)

    xml = '''
    <model><model2>1.1</model2></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel2(text=1.1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_union_list():
    class TestModel(BaseXmlModel, tag='model'):
        sublements: List[Union[int, float]] = element(tag='model1')

    xml = '''
    <model>
        <model1>1</model1>
        <model1>inf</model1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=[1, float('inf')],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_model_union_list():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        element1: float

    class TestModel(BaseXmlModel, tag='model'):
        sublements: List[Union[SubModel1, SubModel2]] = element()

    xml = '''
    <model>
        <model1 attr1="1"/>
        <model2>inf</model2>
        <model1 attr1="2"/>
        <model2>-inf</model2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=[
            SubModel1(attr1=1),
            SubModel2(element1=float('inf')),
            SubModel1(attr1=2),
            SubModel2(element1=float('-inf')),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_union_tuple():
    class TestModel(BaseXmlModel, tag='model'):
        sublements: Tuple[Union[int, float], str, Union[int, float]] = element(tag='model1')

    xml = '''
    <model>
        <model1>inf</model1>
        <model1>text</model1>
        <model1>1</model1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        sublements=(float('inf'), 'text', 1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_union():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        element1: float

    class TestModel(RootXmlModel, tag='model'):
        root: Union[SubModel1, SubModel2]

    xml = '''
    <model>
        <model2>inf</model2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(SubModel2(element1=float('inf')))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_union_list():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        element1: float

    class TestModel(RootXmlModel, tag='model'):
        root: Union[SubModel1, SubModel2]

    xml = '''
    <model>
        <model2>inf</model2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(SubModel2(element1=float('inf')))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_definition_errors():
    with pytest.raises(TypeError):
        class SubModel(BaseXmlModel):
            pass

        class TestModel(BaseXmlModel):
            field1: Union[int, SubModel]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python 3.10 and above")
def test_union_type():
    class TestModel(BaseXmlModel, tag='model'):
        text: int | float | str

    xml = '''
    <model>text</model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(text='text')

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python 3.10 and above")
def test_model_union_type():
    class SubModel1(BaseXmlModel, tag='model1'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='model2'):
        text: float

    class TestModel(BaseXmlModel, tag='model'):
        field1: SubModel1 | SubModel2 = element()

    xml = '''
    <model><model1 attr1="1"></model1></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel1(attr1=1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)

    xml = '''
    <model><model2>inf</model2></model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=SubModel2(text=float('inf')),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.parametrize('type', ['type1', 'type2', 'type3'])
def test_attribute_discriminated_model_tagged_union(type: str):
    class SubModel1(BaseXmlModel, tag='submodel'):
        type: Literal['type1'] = attr()
        text: str

    class SubModel2(BaseXmlModel, tag='submodel'):
        type: Literal['type2', 'type3'] = attr()
        text: str

    class TestModel(RootXmlModel, tag='model'):
        root: Union[SubModel1, SubModel2] = Field(..., discriminator='type')

    xml = '''
    <model>
        <submodel type="{type}">text</submodel>
    </model>
    '''.format(type=type)

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel.model_validate(dict(type=type, text='text'))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_namespaced_attribute_discriminated_model_tagged_union():
    NSMAP = {'tst': 'http://test.org'}

    class SubModel1(BaseXmlModel, tag='submodel', ns='tst', nsmap=NSMAP):
        type: Literal['type1'] = attr(ns='tst')
        text: str

    class SubModel2(BaseXmlModel, tag='submodel', ns='tst', nsmap=NSMAP):
        type: Literal['type2'] = attr(ns='tst')
        text: str

    class TestModel(RootXmlModel, tag='model'):
        root: Union[SubModel1, SubModel2] = element(discriminator='type')

    xml = '''
    <model>
        <tst:submodel tst:type="type2" xmlns:tst="http://test.org">text</tst:submodel>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel.model_validate(dict(type='type2', text='text'))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_path_discriminated_model_tagged_union():
    class SubModel1(BaseXmlModel, tag='submodel1'):
        type: Literal['type1'] = attr()
        text: str

    class SubModel2(BaseXmlModel, tag='submodel2'):
        type: Literal['type2'] = attr()
        text: str

    class TestModel(RootXmlModel, tag='model'):
        root: Union[SubModel1, SubModel2] = Field(..., discriminator='type')

    xml = '''
    <model>
        <submodel2 type="type2">text</submodel2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel.model_validate(dict(type='type2', text='text'))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above")
def test_tagged_union_collection():
    from typing import Annotated

    class SubModel1(BaseXmlModel):
        type: Literal['type1'] = attr()
        data: int

    class SubModel2(BaseXmlModel):
        type: Literal['type2'] = attr()
        data: str

    class TestModel(BaseXmlModel, tag='model'):
        collection: List[Annotated[Union[SubModel1, SubModel2], Field(discriminator='type')]] = element('submodel')

    xml = '''
    <model>
        <submodel type="type1">1</submodel>
        <submodel type="type2">a</submodel>
        <submodel type="type2">b</submodel>
        <submodel type="type1">2</submodel>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        collection=[
            SubModel1(type='type1', data='1'),
            SubModel2(type='type2', data='a'),
            SubModel2(type='type2', data='b'),
            SubModel1(type='type1', data='2'),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_union_snapshot():
    class SubModel1(BaseXmlModel, tag='submodel'):
        attr1: int = attr()

    class SubModel2(BaseXmlModel, tag='submodel'):
        attr1: str = attr()

    class TestModel(BaseXmlModel, tag='model'):
        element1: Union[SubModel1, SubModel2]

    xml = '''
    <model>
        <submodel attr1="a" />
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(element1=SubModel2(attr1="a"))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
