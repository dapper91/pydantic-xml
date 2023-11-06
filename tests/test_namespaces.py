from typing import Dict, List, Tuple

import pytest
from helpers import assert_xml_equal, is_lxml_native

from pydantic_xml import BaseXmlModel, attr, element, wrapped


def test_default_namespaces():
    class TestSubMode2(BaseXmlModel, nsmap={'': 'http://test2.org', 'tst': 'http://test3.org'}):
        attr1: int = attr()
        attr2: int = attr(ns='tst')
        element: str = element()

    class TestSubModel1(BaseXmlModel):
        submodel2: TestSubMode2 = element(nsmap={'': 'http://test2.org'})

    class TestModel(BaseXmlModel, tag='model'):
        submodel1: TestSubModel1 = element(nsmap={'': 'http://test1.org'})

    xml = '''
    <model>
        <submodel1 xmlns="http://test1.org">
            <submodel2 xmlns="http://test2.org" xmlns:tst="http://test3.org" attr1="1" tst:attr2="2">
                <element>value</element>
            </submodel2>
        </submodel1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        submodel1=TestSubModel1(submodel2=TestSubMode2(element='value', attr1=1, attr2=2)),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


@pytest.mark.skipif(not is_lxml_native(), reason='not lxml used')
def test_lxml_default_namespace_serialisation():
    class TestSubModel(BaseXmlModel, tag='submodel', ns='', nsmap={'': 'http://test3.org', 'tst': 'http://test4.org'}):
        attr1: int = attr()
        attr2: int = attr(ns='tst')
        element1: str = element(ns='')

    class TestModel(BaseXmlModel, tag='model', ns='', nsmap={'': 'http://test1.org', 'tst': 'http://test2.org'}):
        attr1: int = attr()
        attr2: int = attr(ns='tst')
        element1: str = element()

        submodel: TestSubModel = element()

    xml = '''
    <model xmlns="http://test1.org" xmlns:tst="http://test2.org" attr1="1" tst:attr2="2">
        <element1>value</element1>
        <submodel xmlns="http://test3.org" xmlns:tst="http://test4.org" attr1="1" tst:attr2="2">
            <element1>value</element1>
        </submodel>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1='value',
        attr1=1,
        attr2=2,
        submodel=TestSubModel(element1='value', attr1=1, attr2=2),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()

    actual_xml_normalized = actual_xml.decode().replace('\n', '').replace(' ', '')
    expected_xml_normalized = xml.replace('\n', '').replace(' ', '')
    assert actual_xml_normalized == expected_xml_normalized


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


def test_submodel_namespaces():
    class TestSubModel(BaseXmlModel, tag='submodel'):
        attr1: int = attr()
        attr2: int = attr()
        element1: str = element()

    class TestModel(BaseXmlModel, tag='model'):
        submodel: TestSubModel = element(ns='tst', nsmap={'tst': 'http://test1.org'})

    xml = '''
    <model>
        <tst:submodel xmlns:tst="http://test1.org" attr1="1" attr2="2">
            <element1>value</element1>
        </tst:submodel>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        submodel=TestSubModel(element1='value', attr1=1, attr2=2),
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
    class TestSubModel1(BaseXmlModel, ns='tst1'):
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
    class TestSubModel1(BaseXmlModel, ns='tst1'):
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


def test_model_inheritance():
    class BaseTestModel(BaseXmlModel, tag='model', ns='tst', nsmap={'tst': 'http://test1.org'}):
        attr1: int = attr()
        element1: str = element()

    class TestModel(BaseTestModel):
        pass

    xml1 = '''
    <tst:model xmlns:tst="http://test1.org" attr1="1">
        <tst:element1>value</tst:element1>
    </tst:model>
    '''

    actual_obj = TestModel.from_xml(xml1)
    expected_obj = TestModel(attr1=1, element1='value')

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml1)


def test_model_inheritance_params_redefinition():
    class BaseTestModel(BaseXmlModel, tag='base-model', ns='bs', nsmap={'bs': 'http://base.org'}):
        attr1: int = attr()
        element1: str = element()

    class TestModel(BaseTestModel, tag='model', ns='tst', nsmap={'tst': 'http://test1.org'}):
        pass

    xml1 = '''
    <tst:model xmlns:tst="http://test1.org" attr1="1">
        <tst:element1>value</tst:element1>
    </tst:model>
    '''

    actual_obj = TestModel.from_xml(xml1)
    expected_obj = TestModel(attr1=1, element1='value')

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml1)


def test_submodel_namespaces_default_namespace_inheritance():
    class TestSubModel(BaseXmlModel, tag='submodel', ns='', nsmap={'': 'http://test2.org'}):
        attr1: int = attr()
        attr2: int = attr()
        element1: str = element()

    class TestModel(BaseXmlModel, tag='model', ns='tst', nsmap={'tst': 'http://test1.org'}):
        submodel: TestSubModel

    xml = '''
    <tst:model xmlns:tst="http://test1.org">
        <submodel xmlns="http://test2.org" attr1="1" attr2="2">
            <element1>value</element1>
        </submodel>
    </tst:model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        submodel=TestSubModel(element1='value', attr1=1, attr2=2),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
