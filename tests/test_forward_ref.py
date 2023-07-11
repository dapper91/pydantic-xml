from typing import Generic, List, NewType, Optional, Tuple, TypeVar, Union

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, wrapped


def test_primitive_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        data: 'CustomInt'
        attr1: 'CustomInt' = attr()
        attr2: Optional['CustomInt'] = attr(default=None)
        element1: 'CustomInt' = element()

    CustomInt = NewType('CustomInt', int)

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1 attr1="1">1<element1>1</element1></model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=CustomInt(1), attr1=CustomInt(1), element1=CustomInt(1))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml)


def test_submodel_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        model1: 'TestSubModel' = element()

    class TestSubModel(BaseXmlModel, tag='model2'):
        attr1: str = attr()

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <model2 attr1="1"></model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model1=TestSubModel(attr1='1'))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_recursive_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        model1: Optional['TestModel'] = element(default=None)

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <model1></model1>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model1=TestModel())

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_list_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        field1: List['CustomInt'] = element()

    CustomInt = NewType('CustomStr', int)

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <field1>1</field1>
        <field1>2</field1>
        <field1>3</field1>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=[
            CustomInt(1), CustomInt(2), CustomInt(3),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_list_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        models: List['TestSubModel'] = element()

    class TestSubModel(BaseXmlModel, tag='model2'):
        attr1: str = attr()

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <model2 attr1="1"></model2>
        <model2 attr1="2"></model2>
        <model2 attr1="3"></model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        models=[
            TestSubModel(attr1='1'), TestSubModel(attr1='2'), TestSubModel(attr1='3'),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_tuple_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        field1: Tuple['CustomInt', 'CustomInt'] = element()

    CustomInt = NewType('CustomInt', int)

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <field1>1</field1>
        <field1>2</field1>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        field1=[
            CustomInt(1), CustomInt(2),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_tuple_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        models: Tuple['TestSubModel', 'TestSubModel'] = element()

    class TestSubModel(BaseXmlModel, tag='model2'):
        attr1: str = attr()

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <model2 attr1="1"></model2>
        <model2 attr1="2"></model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        models=(
            TestSubModel(attr1='1'), TestSubModel(attr1='2'),
        ),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_primitive_union_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        field1: Union['CustomInt', 'CustomFloat'] = element()
        field2: Union['CustomInt', 'CustomFloat'] = element()

    CustomInt = NewType('CustomInt', int)
    CustomFloat = NewType('CustomStr', float)

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <field1>1</field1>
        <field2>1.1</field2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(field1=CustomInt(1), field2=CustomFloat(1.1))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_submodel_union_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        model1: Union['TestSubModel1', 'TestSubModel2'] = element()
        model2: Union['TestSubModel1', 'TestSubModel2'] = element()

    class TestSubModel1(BaseXmlModel, tag='model2'):
        attr1: int = attr()

    class TestSubModel2(BaseXmlModel, tag='model3'):
        attr1: str = attr()

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <model2 attr1="1"></model2>
        <model3 attr1="a"></model3>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model1=TestSubModel1(attr1='1'), model2=TestSubModel2(attr1='a'))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_root_model_forward_ref():
    class TestModel(RootXmlModel, tag='model1'):
        root: 'TestSubModel'

    class TestSubModel(RootXmlModel, tag='model2'):
        root: int

    TestModel.model_rebuild(_types_namespace=locals())

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


def test_wrapped_primitive_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        data: 'CustomInt' = wrapped('model2')
        attr1: 'CustomInt' = wrapped('model2', attr())
        element1: 'CustomInt' = wrapped('model2', element())

    CustomInt = NewType('CustomInt', int)

    TestModel.model_rebuild(_types_namespace=locals())

    xml = '''
    <model1>
        <model2 attr1="2">1<element1>3</element1></model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=1, attr1=2, element1=3)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_model_forward_ref():
    class TestModel(BaseXmlModel, tag='model1'):
        data: 'TestSubModel' = wrapped('model2/model3', element())
        empty: Optional['TestSubModel'] = wrapped('model2/model4', element(default=None))

    class TestSubModel(BaseXmlModel, tag='model4'):
        attr1: int = attr()

    TestModel.model_rebuild(_types_namespace=locals())

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


def test_generic_model_forward_ref():
    GenericType1 = TypeVar('GenericType1')

    class GenericModel(BaseXmlModel, Generic[GenericType1], tag='model1'):
        attr1: GenericType1 = attr()
        attr2: 'CustomFloat' = attr()

    globals()['CustomFloat'] = NewType('CustomFloat', float)
    GenericModel.model_rebuild()

    xml1 = '''
    <model1 attr1="1" attr2="2.2"/>
    '''

    TestModel = GenericModel[int]

    del globals()['CustomFloat']

    actual_obj = TestModel.from_xml(xml1)
    expected_obj = TestModel(attr1=1, attr2=2.2)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml1)
