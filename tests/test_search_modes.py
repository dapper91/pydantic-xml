from typing import Dict, List, Optional, Tuple

import pydantic
import pytest
from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, wrapped


def test_optional_field():
    class TestModel(BaseXmlModel, tag='model'):
        element1: Optional[int] = element(tag='element1')
        element2: int = element(tag='element2')

    xml = '''
    <model>
        <element2>2</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=None,
        element2=2,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml)


def test_strict_mode_error():
    class TestModel(BaseXmlModel, tag='model', search_mode='strict'):
        element1: int = element(tag='element1')
        element2: int = element(tag='element2')

    xml = '''
    <model>
        <element1>1</element1>
        <ignore/>
        <element2>2</element2>
    </model>
    '''

    with pytest.raises(pydantic.ValidationError) as err:
        TestModel.from_xml(xml)

    ex = err.value
    assert len(ex.errors()) == 1

    error = ex.errors()[0]
    assert error['loc'] == ('element2',)
    assert error['type'] == 'value_error.missing'


def test_ordered_mode():
    class TestModel(BaseXmlModel, tag='model', search_mode='ordered'):
        element1: int = element(tag='element')
        element2: int = element(tag='element')
        element_tuple: Tuple[int, int] = element(tag='element')
        element_list: List[int] = element(tag='element')

    src_xml = '''
    <model>
        <ignore/>
        <element>1</element>
        <ignore/>
        <element>2</element>
        <ignore/>
        <ignore/>
        <element>3</element>
        <ignore/>
        <element>4</element>
        <ignore/>
        <ignore/>
        <element>5</element>
        <ignore/>
        <element>6</element>
    </model>
    '''

    expected_xml = '''
    <model>
        <element>1</element>
        <element>2</element>
        <element>3</element>
        <element>4</element>
        <element>5</element>
        <element>6</element>
    </model>
    '''

    actual_obj = TestModel.from_xml(src_xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
        element_tuple=(3, 4),
        element_list=[5, 6],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, expected_xml)


def test_ordered_mode_error():
    class TestModel(BaseXmlModel, tag='model', search_mode='ordered'):
        element1: int = element(tag='element1')
        element2: int = element(tag='element2')
        element3: int = element(tag='element1')

    xml = '''
    <model>
        <element1>1</element1>
        <element1>2</element1>
        <element2>3</element2>
    </model>
    '''

    with pytest.raises(pydantic.ValidationError) as e:
        TestModel.from_xml(xml)

    errors = e.value.errors()
    assert len(errors) == 1
    assert errors[0] == {'loc': ('element3',), 'msg': 'field required', 'type': 'value_error.missing'}


def test_unordered_mode():
    class TestModel(BaseXmlModel, tag='model', search_mode='unordered'):
        element1: int = element(tag='element1')
        element2: int = element(tag='element2')
        element_tuple: Tuple[int, int] = element(tag='element3')
        element_list: List[int] = element(tag='element4')

    src_xml = '''
        <model>
            <element3>3</element3>
            <element2>2</element2>
            <element3>4</element3>
            <element4>5</element4>
            <element1>1</element1>
            <element4>6</element4>
        </model>
    '''

    expected_xml = '''
        <model>
            <element1>1</element1>
            <element2>2</element2>
            <element3>4</element3>
            <element3>3</element3>
            <element4>5</element4>
            <element4>6</element4>
        </model>
    '''

    actual_obj = TestModel.from_xml(src_xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
        element_tuple=(4, 3),
        element_list=[5, 6],
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, expected_xml)


def test_unordered_mode_error():
    class TestModel(BaseXmlModel, tag='model', search_mode='unordered'):
        element1: int = element(tag='element1')
        element2: int = element(tag='element2')
        element3: int = element(tag='element2')

    xml = '''
    <model>
        <element2>2</element2>
        <element1>1</element1>
    </model>
    '''

    with pytest.raises(pydantic.ValidationError) as e:
        TestModel.from_xml(xml)

    errors = e.value.errors()
    assert len(errors) == 1
    assert errors[0] == {'loc': ('element3',), 'msg': 'field required', 'type': 'value_error.missing'}


def test_submodel_mode():
    class TestSubModel(BaseXmlModel, tag='model', search_mode='unordered'):
        element3: int = element(tag='element3')
        element4: int = element(tag='element4')

    class TestModel(BaseXmlModel, tag='model', search_mode='strict'):
        element1: int = element(tag='element1')
        element2: TestSubModel = element(tag='element2')

    src_xml = '''
    <model>
        <element1>1</element1>
        <element2>
            <element4>4</element4>
            <element3>3</element3>
        </element2>
    </model>
    '''

    expected_xml = '''
    <model>
        <element1>1</element1>
        <element2>
            <element3>3</element3>
            <element4>4</element4>
        </element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(src_xml)
    expected_obj = TestModel(
        element1=1,
        element2=TestSubModel(
            element3=3,
            element4=4,
        ),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, expected_xml)


def test_optional_lookahead():
    class TestModel(BaseXmlModel, tag='model', search_mode='ordered'):
        element1: Optional[int] = element(tag='element1')
        element2: int = element(tag='element2')

    xml = '''
    <model>
        <element2>2</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element2=2,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml)


def test_optional_elements_sequential_extraction():
    class TestModel(BaseXmlModel, tag='model'):
        element1: int = element(tag='element1')
        element2: Optional[int] = element(tag='element2')
        element3: int = element(tag='element3')
        element4: int = element(tag='element2')

    xml = '''
    <model>
        <element1>1</element1>
        <element3>3</element3>
        <element2>4</element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=1,
        element3=3,
        element4=4,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml)


def test_multiple_text_error():
    class TestModel(BaseXmlModel, tag='model'):
        text1: int
        text2: int  # text already bound to 'text1' field

    xml = '''
    <model>1</model>
    '''

    with pytest.raises(pydantic.ValidationError) as err:
        TestModel.from_xml(xml)

    error: pydantic.ValidationError = err.value
    assert len(error.errors()) == 1
    assert error.errors()[0]['loc'] == ('text2',)
    assert error.errors()[0]['type'] == 'value_error.missing'


def test_multiple_attr_error():
    class TestModel(BaseXmlModel, tag='model'):
        attr1: int = attr(name='attr')
        attr2: int = attr(name='attr')  # attr already bound to 'attr1' field

    xml = '''
    <model attr="1"/>
    '''

    with pytest.raises(pydantic.ValidationError) as err:
        TestModel.from_xml(xml)

    error: pydantic.ValidationError = err.value
    assert len(error.errors()) == 1
    assert error.errors()[0]['loc'] == ('attr2',)
    assert error.errors()[0]['type'] == 'value_error.missing'


def test_mapping_and_attr_error():
    class TestModel(BaseXmlModel, tag='model'):
        attrs: Dict[str, str]
        attr1: int = attr(name='attr')  # attr already bound to 'attrs' field

    xml = '''
    <model attr="1"/>
    '''

    with pytest.raises(pydantic.ValidationError) as err:
        TestModel.from_xml(xml)

    error: pydantic.ValidationError = err.value
    assert len(error.errors()) == 1
    assert error.errors()[0]['loc'] == ('attr1',)
    assert error.errors()[0]['type'] == 'value_error.missing'


def test_doc_with_comments():
    class TestModel(BaseXmlModel, tag='model'):
        element1: int = element()
        element2: int = element()

    xml = '''
    <!--comment0-->
    <model>
        <!--comment1-->
        <element1>1<!--comment1.1--></element1>
        <!--comment2-->
        <element2>2<!--comment2.1--></element2>
        <!--comment3-->
    </model>
    <!--comment4-->
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapper_strict_mode():
    class TestModel(BaseXmlModel, tag='model'):
        element1: int = wrapped('element1', element(tag='subelement'))
        element2: int = wrapped('element1', element(tag='subelement'))
        element3: int = wrapped('element2', element(tag='subelement'))

    xml = '''
    <model>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <element2>
            <subelement>3</subelement>
        </element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
        element3=3,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, xml)


def test_wrapper_strict_mode_error():
    class TestModel(BaseXmlModel, tag='model'):
        element1: int = wrapped('element1', element(tag='subelement'))
        element2: int = wrapped('element2', element(tag='subelement'))
        element3: int = wrapped('element1', element(tag='subelement'))

    xml = '''
    <model>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <element2>
            <subelement>3</subelement>
        </element2>
    </model>
    '''

    with pytest.raises(pydantic.ValidationError) as e:
        TestModel.from_xml(xml)

    errors = e.value.errors()
    assert len(errors) == 1
    assert errors[0] == {'loc': ('element3',), 'msg': 'field required', 'type': 'value_error.missing'}


def test_wrapper_ordered_mode():
    class TestModel(BaseXmlModel, tag='model', search_mode='ordered'):
        element1: int = wrapped('element1', element(tag='subelement'))
        element2: int = wrapped('element1', element(tag='subelement'))
        element3: int = wrapped('element2', element(tag='subelement'))

    src_xml = '''
    <model>
        <ignore/>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <ignore/>
        <ignore/>
        <element2>
            <subelement>3</subelement>
        </element2>
        <ignore/>
    </model>
    '''

    expected_xml = '''
    <model>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <element2>
            <subelement>3</subelement>
        </element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(src_xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
        element3=3,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, expected_xml)


def test_wrapper_ordered_mode_error():
    class TestModel(BaseXmlModel, tag='model', search_mode='ordered'):
        element1: int = wrapped('element1', element(tag='subelement'))
        element2: int = wrapped('element1', element(tag='subelement'))
        element3: int = wrapped('element2', element(tag='subelement'))

    xml = '''
    <model>
        <element2>
            <subelement>3</subelement>
        </element2>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <ignore/>
    </model>
    '''

    with pytest.raises(pydantic.ValidationError) as e:
        TestModel.from_xml(xml)

    errors = e.value.errors()
    assert len(errors) == 1
    assert errors[0] == {'loc': ('element3',), 'msg': 'field required', 'type': 'value_error.missing'}


def test_wrapper_unordered_mode():
    class TestModel(BaseXmlModel, tag='model', search_mode='unordered'):
        element1: int = wrapped('element1', element(tag='subelement'))
        element2: int = wrapped('element1', element(tag='subelement'))
        element3: int = wrapped('element2', element(tag='subelement'))

    src_xml = '''
    <model>
        <ignore/>
        <element2>
            <subelement>3</subelement>
        </element2>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <ignore/>
        <ignore/>
        <ignore/>
    </model>
    '''

    expected_xml = '''
    <model>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <element2>
            <subelement>3</subelement>
        </element2>
    </model>
    '''

    actual_obj = TestModel.from_xml(src_xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
        element3=3,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml(skip_empty=True)
    assert_xml_equal(actual_xml, expected_xml)


def test_wrapper_unordered_mode_error():
    class TestModel(BaseXmlModel, tag='model', search_mode='unordered'):
        element1: int = wrapped('element1', element(tag='subelement'))
        element2: int = wrapped('element2', element(tag='subelement'))
        element3: int = wrapped('element1', element(tag='subelement'))

    xml = '''
    <model>
        <ignore/>
        <element2>
            <subelement>3</subelement>
        </element2>
        <element1>
            <subelement>1</subelement>
            <subelement>2</subelement>
        </element1>
        <ignore/>
        <ignore/>
        <ignore/>
    </model>
    '''

    with pytest.raises(pydantic.ValidationError) as e:
        TestModel.from_xml(xml)

    errors = e.value.errors()
    assert len(errors) == 1
    assert errors[0] == {'loc': ('element3',), 'msg': 'field required', 'type': 'value_error.missing'}
