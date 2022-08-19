from typing import Dict, List, Tuple

import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, wrapped


@pytest.mark.parametrize(
    'model_ns, element_ns, expected_model_ns, expected_element_ns',
    [
        ('tst1', 'tst2', 'tst1', 'tst2'),
        (None, 'tst2', None, 'tst2'),
        ('tst1', None, 'tst1', 'tst1'),
        (None, None, None, None),
    ],
)
def test_elements_namespaces(model_ns, element_ns, expected_model_ns, expected_element_ns):
    class TestModel(
        BaseXmlModel,
        tag='model',
        ns=model_ns,
        nsmap={'tst1': 'http://test1.org', 'tst2': 'http://test2.org'},
    ):
        element1: str = element(ns=element_ns)

    xml = '''
    <{ns_pref1}model xmlns:tst1="http://test1.org" xmlns:tst2="http://test2.org">
        <{ns_pref2}element1>value</{ns_pref2}element1>
    </{ns_pref1}model>
    '''.format(
        ns_pref1=f"{expected_model_ns}:" if expected_model_ns else '',
        ns_pref2=f"{expected_element_ns}:" if expected_element_ns else '',
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1="value",
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.parametrize(
    'ns_attrs, model_ns, attr_ns, expected_model_ns, expected_attr_ns',
    [
        (True, 'tst1', 'tst2', 'tst1', 'tst2'),
        (True, 'tst1', None, 'tst1', 'tst1'),
        (True, None, 'tst2', None, 'tst2'),
        (False, 'tst1', 'tst2', 'tst1', 'tst2'),
        (False, 'tst1', None, 'tst1', None),
        (False, None, 'tst2', None, 'tst2'),
        (False, None, None, None, None),
    ],
)
def test_attrs_namespaces(ns_attrs, model_ns, attr_ns, expected_model_ns, expected_attr_ns):
    class TestModel(
        BaseXmlModel,
        tag='model',
        ns=model_ns,
        nsmap={'tst1': 'http://test1.org', 'tst2': 'http://test2.org'},
        ns_attrs=ns_attrs,
    ):
        attr1: str = attr(ns=attr_ns)

    xml = '''
    <{ns_pref1}model {ns_pref2}attr1="string1" xmlns:tst1="http://test1.org" xmlns:tst2="http://test2.org"/>
    '''.format(
        ns_pref1=f"{expected_model_ns}:" if expected_model_ns else '',
        ns_pref2=f"{expected_attr_ns}:" if expected_attr_ns else '',
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        attr1='string1',
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.parametrize(
    'inherit_ns, model_ns, submodel_ns, element_ns, expected_model_ns, expected_submodel_ns',
    [
        (True, 'tst1', 'tst2', 'tst3', 'tst1', 'tst3'),
    ],
)
def test_namespace_inheritance(
    inherit_ns, model_ns, submodel_ns, element_ns, expected_model_ns, expected_submodel_ns,
):
    class TestSubModel(BaseXmlModel, ns=submodel_ns, inherit_ns=inherit_ns):
        element: float = element()

    class TestModel(
        BaseXmlModel,
        tag='model1',
        ns=model_ns,
        nsmap={'tst1': 'http://test1.org', 'tst2': 'http://test2.org', 'tst3': 'http://test3.org'},
    ):
        model: TestSubModel = element(tag='model2', ns=element_ns)

    xml = '''
        <{ns_pref1}model1 xmlns:tst1="http://test1.org" xmlns:tst2="http://test2.org" xmlns:tst3="http://test3.org">
            <{ns_pref2}model2>
                <{ns_pref2}element>1.1</{ns_pref2}element>
            </{ns_pref2}model2>
        </{ns_pref1}model1>
    '''.format(
        ns_pref1=f"{expected_model_ns}:" if expected_model_ns else "",
        ns_pref2=f"{expected_submodel_ns}:" if expected_submodel_ns else "",
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model=TestSubModel(element=1.1),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_recursive_namespace_inheritance():
    class TestSubModel3(BaseXmlModel, tag='model4', inherit_ns=True):
        element: str = element()

    class TestSubModel2(BaseXmlModel, tag='model3', ns='tst2', nsmap={'tst2': 'http://test.org'}):
        element: TestSubModel3

    class TestSubModel1(BaseXmlModel, tag='model2'):
        element: TestSubModel2

    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap={'tst1': 'http://test.org'}):
        element: TestSubModel1

    xml = '''
        <tst1:model1 xmlns:tst1="http://test.org">
            <model2>
                <tst2:model3 xmlns:tst2="http://test.org">
                    <tst2:model4>
                        <tst2:element>string1</tst2:element>
                    </tst2:model4>
                </tst2:model3>
            </model2>
        </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element=TestSubModel1(
            element=TestSubModel2(
                element=TestSubModel3(element="string1"),
            ),
        ),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.parametrize(
    'ns_attrs, expected_attr_ns',
    [
        (True, 'tst1'),
        (False, None),
    ],
)
def test_mapping_namespace_inheritance(ns_attrs, expected_attr_ns):
    class TestModel(BaseXmlModel, tag='model', ns='tst1', nsmap={'tst1': 'http://test.org'}, ns_attrs=ns_attrs):
        attrs: Dict[str, int]

    xml = '''
        <tst1:model {ns_pref1}attr1="1" {ns_pref1}attr2="2" xmlns:tst1="http://test.org"/>
    '''.format(
        ns_pref1=f"{expected_attr_ns}:" if expected_attr_ns else '',
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        attrs={
            'attr1': 1,
            'attr2': 2,
        },
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.parametrize(
    'inherit_ns, model_ns, submodel_ns, element_ns, expected_model_ns, expected_submodel_ns, expected_element_ns',
    [
        (True, 'tst1', 'tst2', 'tst3', 'tst1', 'tst3', 'tst2'),
        (True, 'tst1', None, 'tst3', 'tst1', 'tst3', 'tst3'),
        (True, 'tst1', None, None, 'tst1', 'tst1', 'tst1'),
        (False, 'tst1', None, 'tst3', 'tst1', 'tst3', None),
        (False, None, None, None, None, None, None),
    ],
)
def test_homogeneous_collections_namespace_inheritance(
    inherit_ns, model_ns, submodel_ns, element_ns, expected_model_ns, expected_submodel_ns, expected_element_ns,
):
    class TestSubModel(BaseXmlModel, ns=submodel_ns, inherit_ns=inherit_ns):
        element: float = element()

    class RootModel(
        BaseXmlModel,
        tag='model1',
        ns=model_ns,
        nsmap={'tst1': 'http://test1.org', 'tst2': 'http://test2.org', 'tst3': 'http://test3.org'},
    ):
        elements: List[TestSubModel] = element(tag='model2', ns=element_ns)

    xml = '''
        <{ns_pref1}model1 xmlns:tst1="http://test1.org" xmlns:tst2="http://test2.org" xmlns:tst3="http://test3.org">
            <{ns_pref2}model2>
                <{ns_pref3}element>1.1</{ns_pref3}element>
            </{ns_pref2}model2>
            <{ns_pref2}model2>
                <{ns_pref3}element>2.2</{ns_pref3}element>
            </{ns_pref2}model2>
        </{ns_pref1}model1>
    '''.format(
        ns_pref1=f"{expected_model_ns}:" if expected_model_ns else "",
        ns_pref2=f"{expected_submodel_ns}:" if expected_submodel_ns else "",
        ns_pref3=f"{expected_element_ns}:" if expected_element_ns else "",
    )

    actual_obj = RootModel.from_xml(xml)
    expected_obj = RootModel(
        elements=[
            TestSubModel(element=1.1),
            TestSubModel(element=2.2),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_heterogeneous_collections_namespace_inheritance():
    class TestSubModel1(BaseXmlModel, ns_attrs=True, inherit_ns=True):
        attr1: int = attr()
        element: float = element()

    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap={'tst1': 'http://test.org'}):
        elements: Tuple[TestSubModel1, TestSubModel1] = element(tag='model2', ns='tst1')

    xml = '''
        <tst1:model1 xmlns:tst1="http://test.org">
            <tst1:model2 tst1:attr1="1">
                <tst1:element>1.1</tst1:element>
            </tst1:model2>
            <tst1:model2 tst1:attr1="2">
                <tst1:element>2.2</tst1:element>
            </tst1:model2>
        </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        elements=(TestSubModel1(attr1=1, element=1.1), TestSubModel1(attr1=2, element=2.2)),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapper_namespaces():
    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap={'tst1': 'http://test1.org'}):
        data: int = wrapped('model2/model3', ns='tst2', nsmap={'tst2': 'http://test2.org'})

    xml = '''
    <tst1:model1 xmlns:tst1="http://test1.org">
        <tst2:model2 xmlns:tst2="http://test2.org">
            <tst2:model3>1</tst2:model3>
        </tst2:model2>
    </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapper_namespace_inheritance():
    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap={'tst1': 'http://test1.org'}):
        data: int = wrapped('model2/model3/model4')

    xml = '''
    <tst1:model1 xmlns:tst1="http://test1.org">
        <tst1:model2 >
            <tst1:model3>
                <tst1:model4>1</tst1:model4>
            </tst1:model3>
        </tst1:model2>
    </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_homogeneous_collection_wrapper_namespace_inheritance():
    class TestSubModel1(BaseXmlModel, inherit_ns=True):
        data: int

    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap={'tst1': 'http://test1.org'}):
        model3: List[TestSubModel1] = wrapped('model2', element())

    xml = '''
    <tst1:model1 xmlns:tst1="http://test1.org">
        <tst1:model2>
            <tst1:model3>1</tst1:model3>
            <tst1:model3>2</tst1:model3>
        </tst1:model2>
    </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model3=[
            TestSubModel1(data=1),
            TestSubModel1(data=2),
        ],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_heterogeneous_collection_wrapper_namespace_inheritance():
    class TestSubModel1(BaseXmlModel, inherit_ns=True):
        data: int

    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap={'tst1': 'http://test1.org'}):
        model3: Tuple[TestSubModel1, TestSubModel1] = wrapped('model2', element())

    xml = '''
    <tst1:model1 xmlns:tst1="http://test1.org">
        <tst1:model2>
            <tst1:model3>1</tst1:model3>
            <tst1:model3>2</tst1:model3>
        </tst1:model2>
    </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        model3=(
            TestSubModel1(data=1),
            TestSubModel1(data=2),
        ),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_mapping_wrapper_namespace_inheritance():
    class TestModel(BaseXmlModel, tag='model1', ns_attrs=True, ns='tst1', nsmap={'tst1': 'http://test1.org'}):
        attrs: Dict[str, int] = wrapped('model2')

    xml = '''
    <tst1:model1 xmlns:tst1="http://test1.org">
        <tst1:model2 tst1:attr1="1" tst1:attr2="2"/>
    </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        attrs={
            'attr1': 1,
            'attr2': 2,
        },
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
