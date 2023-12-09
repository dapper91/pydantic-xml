from typing import List, Tuple, Union

import pydantic as pd
import pytest

from pydantic_xml import BaseXmlModel, attr, element, wrapped
from tests.helpers import fmt_sourceline


def test_submodel_errors():
    class TestSubModel(BaseXmlModel, tag='submodel'):
        field1: int = element()
        field2: int = element()
        field3: int = element()

    class TestModel(BaseXmlModel, tag='model'):
        submodel: TestSubModel

    xml = '''
        <model>
            <submodel>
                <field1>a</field1>
                <field2>1</field2>
                <field3>b</field3>
            </submodel>
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 2
    assert err.errors() == [
        {
            'input': 'a',
            'loc': ('submodel', 'field1'),
            'msg': f'[line {fmt_sourceline(4)}]: Input should be a valid integer, unable to parse string as an integer',
            'type': 'int_parsing',
            'ctx': {
                'orig': 'Input should be a valid integer, unable to parse string as an integer',
                'sourceline': fmt_sourceline(4),
            },
        },
        {
            'input': 'b',
            'loc': ('submodel', 'field3'),
            'msg': f'[line {fmt_sourceline(6)}]: Input should be a valid integer, unable to parse string as an integer',
            'type': 'int_parsing',
            'ctx': {
                'orig': 'Input should be a valid integer, unable to parse string as an integer',
                'sourceline': fmt_sourceline(6),
            },
        },
    ]


def test_homogeneous_collection_errors():
    class TestSubModel(BaseXmlModel, tag='submodel'):
        attr1: int = attr()

    class TestModel(BaseXmlModel, tag='model'):
        submodel: List[TestSubModel]

    xml = '''
        <model>
            <submodel attr1="a" />
            <submodel attr1="1" />
            <submodel attr1="b" />
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 2
    assert err.errors() == [
        {
            'input': 'a',
            'loc': ('submodel', 0, 'attr1'),
            'msg': f'[line {fmt_sourceline(3)}]: Input should be a valid integer, unable to parse string as an integer',
            'type': 'int_parsing',
            'ctx': {
                'orig': 'Input should be a valid integer, unable to parse string as an integer',
                'sourceline': fmt_sourceline(3),
            },
        },
        {
            'input': 'b',
            'loc': ('submodel', 2, 'attr1'),
            'msg': f'[line {fmt_sourceline(5)}]: Input should be a valid integer, unable to parse string as an integer',
            'type': 'int_parsing',
            'ctx': {
                'orig': 'Input should be a valid integer, unable to parse string as an integer',
                'sourceline': fmt_sourceline(5),
            },
        },
    ]


def test_heterogeneous_collection_errors():
    class TestSubModel(BaseXmlModel, tag='submodel'):
        attrs: Union[int, bool] = wrapped('wrapper')

    class TestModel(BaseXmlModel, tag='model'):
        submodel: Tuple[TestSubModel, TestSubModel, TestSubModel]

    xml = '''
        <model>
            <submodel>
                <wrapper>a</wrapper>
            </submodel>
            <submodel>
                <wrapper>1</wrapper>
            </submodel>
            <submodel>
                <wrapper>b</wrapper>
            </submodel>
        </model>
    '''

    with pytest.raises(pd.ValidationError) as exc:
        TestModel.from_xml(xml)

    err = exc.value
    assert err.title == 'TestModel'
    assert err.error_count() == 4
    assert err.errors() == [
        {
            'input': 'a',
            'loc': ('submodel', 0, 'attrs', 'int'),
            'msg': f'[line {fmt_sourceline(4)}]: Input should be a valid integer, unable to parse string as an integer',
            'type': 'int_parsing',
            'ctx': {
                'orig': 'Input should be a valid integer, unable to parse string as an integer',
                'sourceline': fmt_sourceline(4),
            },
        },
        {
            'input': 'a',
            'loc': ('submodel', 0, 'attrs', 'bool'),
            'msg': f'[line {fmt_sourceline(4)}]: Input should be a valid boolean, unable to interpret input',
            'type': 'bool_parsing',
            'ctx': {
                'orig': 'Input should be a valid boolean, unable to interpret input',
                'sourceline': fmt_sourceline(4),
            },
        },
        {
            'input': 'b',
            'loc': ('submodel', 2, 'attrs', 'int'),
            'msg': f'[line {fmt_sourceline(10)}]: Input should be a valid integer, unable to parse string as an integer',
            'type': 'int_parsing',
            'ctx': {
                'orig': 'Input should be a valid integer, unable to parse string as an integer',
                'sourceline': fmt_sourceline(10),
            },
        },
        {
            'input': 'b',
            'loc': ('submodel', 2, 'attrs', 'bool'),
            'msg': f'[line {fmt_sourceline(10)}]: Input should be a valid boolean, unable to interpret input',
            'type': 'bool_parsing',
            'ctx': {
                'orig': 'Input should be a valid boolean, unable to interpret input',
                'sourceline': fmt_sourceline(10),
            },
        },
    ]
