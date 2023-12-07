from typing import Dict

import pydantic as pd
import pytest

from pydantic_xml import BaseXmlModel, attr, element, wrapped


@pytest.mark.parametrize('search_mode', ['strict', 'ordered', 'unordered'])
def test_extra_forbid(search_mode: str):
    class TestModel(BaseXmlModel, tag='model', extra='forbid', search_mode=search_mode):
        attr1: str = attr()
        field1: str = element()

    xml = '''
        <model attr1="attr value 1" attr2="attr value 2">text value
            <field1>field value 1</field1>
            <field2>field value 2</field2>
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 3
    assert err.errors() == [
        {
            'input': 'text value',
            'loc': (),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
        {
            'input': 'attr value 2',
            'loc': ('@attr2',),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
        {
            'input': 'field value 2',
            'loc': ('field2',),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
    ]


@pytest.mark.parametrize('search_mode', ['strict', 'ordered', 'unordered'])
def test_mapping_extra_forbid(search_mode: str):
    class TestModel(BaseXmlModel, tag='model', extra='forbid', search_mode=search_mode):
        attrs1: Dict[str, str] = element('element1')
        attrs2: Dict[str, str] = element('element2')

    xml = '''
        <model>
            <element1 attr1="attr1 value">text value</element1>
            <element2>
                <subelement>text value</subelement>
            </element2>
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 2
    assert err.errors() == [
        {
            'input': 'text value',
            'loc': ('element1',),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
        {
            'input': 'text value',
            'loc': ('element2', 'subelement'),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
    ]


@pytest.mark.parametrize('search_mode', ['strict', 'ordered', 'unordered'])
def test_submodel_extra_forbid(search_mode: str):
    class TestSubModel(BaseXmlModel, tag='submodel', extra='forbid', search_mode=search_mode):
        attr1: str = attr()
        field1: str = element()

    class TestModel(BaseXmlModel, tag='model', extra='forbid', search_mode=search_mode):
        submodel: TestSubModel

    xml = '''
        <model>
            <submodel attr1="attr value 1" attr2="attr value 2">text value
                <field1>field value 1</field1>
                <field2>field value 2</field2>
            </submodel>
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 3
    assert err.errors() == [
        {
            'input': 'text value',
            'loc': ('submodel',),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
        },
        {
            'input': 'attr value 2',
            'loc': ('submodel', '@attr2'),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
        },
        {
            'input': 'field value 2',
            'loc': ('submodel', 'field2'),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
        },
    ]


@pytest.mark.parametrize('search_mode', ['strict', 'ordered', 'unordered'])
def test_wrapped_extra_forbid(search_mode: str):
    class TestModel(BaseXmlModel, tag='model', extra='forbid', search_mode=search_mode):
        field1: str = wrapped('wrapper1', element(tag='field1'))
        field2: str = wrapped('wrapper2', element(tag='field1'))

    xml = '''
        <model>
            <wrapper1>text value
                <field1>field value 1</field1>
                <field2>field value 2</field2>
            </wrapper1>
            <wrapper2 attr1="attr value 1">
                <field1>field value 1</field1>
                <field2>field value 2</field2>
            </wrapper2>
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 4
    assert err.errors() == [
        {
            'input': 'text value',
            'loc': ('wrapper1',),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
        {
            'input': 'field value 2',
            'loc': ('wrapper1', 'field2'),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
        {
            'input': 'attr value 1',
            'loc': ('wrapper2', '@attr1'),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
        {
            'input': 'field value 2',
            'loc': ('wrapper2', 'field2'),
            'msg': 'Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'url': ANY,
        },
    ]
