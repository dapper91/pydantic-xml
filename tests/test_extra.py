from typing import Dict

import pydantic as pd
import pytest

from pydantic_xml import BaseXmlModel, attr, element, wrapped
from pydantic_xml.element.native import ElementT
from tests.helpers import fmt_sourceline


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
            'msg': f'[line {fmt_sourceline(2)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(2),
            },
        },
        {
            'input': 'attr value 2',
            'loc': ('@attr2',),
            'msg': f'[line {fmt_sourceline(2)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(2),
            },
        },
        {
            'input': 'field value 2',
            'loc': ('field2',),
            'msg': f'[line {fmt_sourceline(4)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(4),
            },
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
            'msg': f'[line {fmt_sourceline(3)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(3),
            },
        },
        {
            'input': 'text value',
            'loc': ('element2', 'subelement'),
            'msg': f'[line {fmt_sourceline(5)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(5),
            },
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
            'msg': f'[line {fmt_sourceline(3)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(3),
            },
        },
        {
            'input': 'attr value 2',
            'loc': ('submodel', '@attr2'),
            'msg': f'[line {fmt_sourceline(3)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(3),
            },
        },
        {
            'input': 'field value 2',
            'loc': ('submodel', 'field2'),
            'msg': f'[line {fmt_sourceline(5)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(5),
            },
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
            'msg': f'[line {fmt_sourceline(3)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(3),
            },
        },
        {
            'input': 'field value 2',
            'loc': ('wrapper1', 'field2'),
            'msg': f'[line {fmt_sourceline(5)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(5),
            },
        },
        {
            'input': 'attr value 1',
            'loc': ('wrapper2', '@attr1'),
            'msg': f'[line {fmt_sourceline(7)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(7),
            },
        },
        {
            'input': 'field value 2',
            'loc': ('wrapper2', 'field2'),
            'msg': f'[line {fmt_sourceline(9)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(9),
            },
        },
    ]


@pytest.mark.parametrize('search_mode', ['strict', 'ordered', 'unordered'])
def test_raw_extra_forbid(search_mode: str):
    class TestModel(
        BaseXmlModel,
        tag='model',
        extra='forbid',
        arbitrary_types_allowed=True,
        search_mode=search_mode
    ):
        field1: ElementT = element("field1")
        field2: ElementT | None = element("field2", default=None)

    xml = '''
        <model>
            <field1>field value 1<nested>nested element field</nested></field1>
            <field2>field value 2</field2>
            <extra>undefined field<nested>nested undefined field</nested></extra>
        </model>
    '''
    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 2
    assert err.errors() == [
        {
            'input': 'undefined field',
            'loc': ('extra',),
            'msg': f'[line {fmt_sourceline(5)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(5),
            },
        },
        {
            'input': 'nested undefined field',
            'loc': ('extra', 'nested'),
            'msg': f'[line {fmt_sourceline(5)}]: Extra inputs are not permitted',
            'type': 'extra_forbidden',
            'ctx': {
                'orig': 'Extra inputs are not permitted',
                'sourceline': fmt_sourceline(5),
            },
        },
    ]
