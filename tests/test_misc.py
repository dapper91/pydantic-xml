import sys
from typing import Dict, List, Optional, Tuple, Union

import pydantic as pd
import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, errors, wrapped
from pydantic_xml.fields import XmlEntityInfo


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


def test_root_not_found_error():
    class TestModel(BaseXmlModel, tag='model'):
        pass

    xml = '''
    <model1/>
    '''

    with pytest.raises(errors.ParsingError) as err:
        TestModel.from_xml(xml)

    assert len(err.value.args) == 1
    assert err.value.args[0] == 'root element not found (actual: model1, expected: model)'


def test_skip_empty():
    class TestSubModel(BaseXmlModel, tag='model'):
        text: Optional[str] = None
        element1: Optional[str] = element(default=None)
        attr1: Optional[str] = attr(default=None)

    class TestModel(BaseXmlModel, tag='model'):
        model: TestSubModel
        list: List[TestSubModel] = []
        tuple: Optional[Tuple[TestSubModel, TestSubModel]] = None
        attrs: Dict[str, str] = {}
        wrapped: Optional[str] = wrapped('envelope', default=None)

    xml = '''
    <model/>
    '''

    obj = TestModel(model=TestSubModel())

    actual_xml = obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_model_level_skip_empty_enable():
    class TestSubModel(BaseXmlModel, tag='submodel', skip_empty=True):
        text: Optional[str]
        attr1: Optional[str] = attr()
        element1: Optional[str] = element()

    class TestModel(BaseXmlModel, tag='model'):
        submodel: TestSubModel
        element1: Optional[str] = element()

    xml = '''
    <model>
        <submodel></submodel>
        <element1></element1>
    </model>
    '''

    obj = TestModel(
        submodel=TestSubModel(
            text=None,
            attr1=None,
            element1=None,
        ),
        element1=None,
    )

    actual_xml = obj.to_xml(skip_empty=False)
    assert_xml_equal(actual_xml, xml.encode())


def test_model_level_skip_empty_disable():
    class TestSubModel(BaseXmlModel, tag='submodel', skip_empty=False):
        text: Optional[str]
        attr1: Optional[str] = attr()
        element1: Optional[str] = element()

    class TestModel(BaseXmlModel, tag='model'):
        submodel: TestSubModel
        element1: Optional[str] = element()

    xml = '''
    <model>
        <submodel attr1=""><element1></element1></submodel>
    </model>
    '''

    obj = TestModel(
        submodel=TestSubModel(
            text=None,
            attr1=None,
            element1=None,
        ),
        element1=None,
    )

    actual_xml = obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_exclude_none():
    class TestSubModel(BaseXmlModel, tag='sub-model'):
        text: Optional[str] = None
        attr1: Optional[str] = attr(default=None)
        element1: Optional[str] = element(default=None)

    class TestModel(BaseXmlModel, tag='model'):
        text: Optional[str] = None
        attr1: Optional[str] = attr(default=None)
        element1: Optional[str] = element(default=None)
        model: TestSubModel

    xml = '''
    <model attr1="attribute">text<element1>element</element1><sub-model/></model>
    '''

    obj = TestModel(
        text='text',
        attr1='attribute',
        element1='element',
        model=TestSubModel(text=None, element1=None, attr1=None),
    )

    actual_xml = obj.to_xml(exclude_none=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_exclude_unset():
    class TestSubModel(BaseXmlModel, tag='sub-model'):
        text: Optional[str] = 'default text'
        element1: Optional[str] = element(default='default element')
        attr1: Optional[str] = attr(default='default attribute')

    class TestModel(BaseXmlModel, tag='model'):
        text: Optional[str] = None
        attr1: Optional[str] = attr(default=None)
        element1: Optional[str] = element(default=None)
        model: TestSubModel

    xml = '''
    <model attr1="attribute">text<element1>element</element1><sub-model/></model>
    '''

    obj = TestModel(
        text='text',
        attr1='attribute',
        element1='element',
        model=TestSubModel(),
    )

    actual_xml = obj.to_xml(exclude_unset=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_exclude_unset_root_model():
    class TestModel(RootXmlModel, tag='model'):
        root: str = 'text'

    xml = '<model/>'
    obj = TestModel()

    actual_xml = obj.to_xml(exclude_unset=True)
    assert_xml_equal(actual_xml, xml.encode())


def test_self_ref_models():
    class TestModel(BaseXmlModel, tag='model'):
        attr1: int = attr()
        element1: float = element()

        model1: Optional['TestModel'] = element(tag='model1', default=None)
        models1: Optional[List['TestModel']] = element(tag='item1', default=None)
        models2: Optional[Tuple['TestModel', 'TestModel']] = element(tag='item2', default=None)

    xml = '''
        <model attr1="1">
            <element1>1.1</element1>
            <model1 attr1="2">
                <element1>2.2</element1>
            </model1>

            <item1 attr1="3">
                <element1>3.3</element1>
            </item1>
            <item1 attr1="4">
                <element1>4.4</element1>
            </item1>
            <item2 attr1="5">
                <element1>5.5</element1>
            </item2>
            <item2 attr1="6">
                <element1>6.6</element1>
            </item2>
        </model>
    '''

    obj = TestModel(
        attr1=1,
        element1=1.1,
        model1=TestModel(
            attr1=2,
            element1=2.2,
        ),
        models1=[
            TestModel(
                attr1=3,
                element1=3.3,
            ),
            TestModel(
                attr1=4,
                element1=4.4,
            ),
        ],
        models2=[
            TestModel(
                attr1=5,
                element1=5.5,
            ),
            TestModel(
                attr1=6,
                element1=6.6,
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


def test_field_serialization_exclude():
    class TestModel(BaseXmlModel, tag='model'):
        element1: int = element(exclude=True)
        element2: int = element(exclude=False)

    xml = '''
        <model>
            <element1>1</element1>
            <element2>2</element2>
        </model>
    '''

    actual_obj: TestModel = TestModel.from_xml(xml)
    expected_obj = TestModel(element1=1, element2=2)
    assert actual_obj == expected_obj

    expected_xml = '''
        <model>
            <element2>2</element2>
        </model>
    '''
    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, expected_xml.encode())


def test_model_params_inheritance():
    class BaseModel(
        BaseXmlModel,
        tag='TestTag',
        ns='TestNamespace',
        nsmap={'TestNamespace': 'value'},
        ns_attrs=True,
        search_mode='ordered',
    ):
        pass

    class TestModel(BaseModel):
        pass

    assert TestModel.__xml_tag__ == BaseModel.__xml_tag__
    assert TestModel.__xml_ns__ == BaseModel.__xml_ns__
    assert TestModel.__xml_nsmap__ == BaseModel.__xml_nsmap__
    assert TestModel.__xml_ns_attrs__ == BaseModel.__xml_ns_attrs__
    assert TestModel.__xml_search_mode__ == BaseModel.__xml_search_mode__


def test_pydantic_validation_context():
    validation_context = {'var1': 1, 'var2': True}

    class TestSubModel(BaseXmlModel, tag='submodel'):
        attr1: int = attr()

        @pd.field_validator('attr1')
        @classmethod
        def validate_field(cls, v: str, info: pd.FieldValidationInfo):
            assert info.context == validation_context
            return v

    class TestModel(BaseXmlModel, tag='model'):
        submodel: TestSubModel
        submodel_union: Union[TestSubModel, TestSubModel]
        submodel_wrapped: TestSubModel = wrapped('wrapper')
        submodel_tuple: Tuple[TestSubModel, TestSubModel]
        submodel_list: List[TestSubModel]

        @pd.field_validator('submodel')
        @classmethod
        def validate_field(cls, v: str, info: pd.FieldValidationInfo):
            assert info.context == validation_context
            return v

    xml = '''
        <model>
            <submodel attr1="0"/>
            <submodel attr1="1"/>
            <wrapper>
                <submodel attr1="2"/>
            </wrapper>
            <submodel attr1="3"/>
            <submodel attr1="4"/>
            <submodel attr1="5"/>
            <submodel attr1="6"/>
            <submodel attr1="7"/>
        </model>
    '''

    TestModel.from_xml(xml, validation_context)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above")
def test_field_info_merge():
    from typing import Annotated

    from annotated_types import Ge, Lt

    class TestModel(BaseXmlModel, tag='root'):
        element1: Annotated[
            int,
            pd.Field(ge=0),
            pd.Field(default=0, lt=100),
            element(nillable=True),
        ] = element(tag='elm', lt=10)

    field_info = TestModel.model_fields['element1']
    assert isinstance(field_info, XmlEntityInfo)
    assert field_info.metadata == [Ge(ge=0), Lt(lt=10)]
    assert field_info.default == 0
    assert field_info.nillable == True
    assert field_info.path == 'elm'

    TestModel.from_xml("<root><elm>0</elm></root>")

    with pytest.raises(pd.ValidationError):
        TestModel.from_xml("<root><elm>-1</elm></root>")
