from typing import Dict, List, Optional

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, attr, element, wrapped


def test_wrapped_primitive_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        element0: str = element(tag='element')
        data: int = wrapped('model2')
        attr1: int = wrapped('model2', attr(name='attr1'))
        element1: int = wrapped('model2', element())

    xml = '''
    <model1>
        <element>text</element>
        <model2 attr1="2">1<element1>3</element1></model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(element0="text", data=1, attr1=2, element1=3)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_path_merge():
    class TestModel(BaseXmlModel, tag='model1'):
        element0: int = element(tag='element0')
        element1: int = element(tag='element1')
        attr0: int = wrapped('element1', attr(name='attr'))
        element2: int = wrapped('element2/element3', element(tag='element4'))
        element3: int = wrapped('element2/element3', element(tag='element5'))
        attr1: int = wrapped('element2/element6', attr(name='attr'))
        element4: int = element(tag='element7')

    xml = '''
    <model1>
        <element0>0</element0>
        <element1 attr="2">1</element1>
        <element2>
            <element3>
                <element4>3</element4>
                <element5>4</element5>
            </element3>
            <element6 attr="5"/>
        </element2>
        <element7>6</element7>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(element0=0, element1=1, attr0=2, element2=3, element3=4, attr1=5, element4=6)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_mult_wrapped_primitive_extraction():
    NSMAP = {
        'tst1': "http://test1.org",
        'tst2': "http://test2.org",
        'tst3': "http://test3.org",
    }

    class TestModel(BaseXmlModel, tag='model1', ns='tst1', nsmap=NSMAP):
        data: int = wrapped('model2', ns='tst2', entity=wrapped('model3', ns='tst3'))

    xml = '''
    <tst1:model1 xmlns:tst1="http://test1.org" xmlns:tst2="http://test2.org" xmlns:tst3="http://test3.org">
        <tst2:model2>
            <tst3:model3>1</tst3:model3>
        </tst2:model2>
    </tst1:model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(data=1)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapper_collection():
    class TestSubModel(BaseXmlModel):
        __root__: int = wrapped('model3/model4', attr(name='attr1'))

    class TestModel(BaseXmlModel, tag='model1'):
        elements: List[TestSubModel] = element(tag='model2')

    xml = '''
    <model1>
        <model2>
            <model3>
                <model4 attr1="1"/>
            </model3>
        </model2>
        <model2>
            <model3>
                <model4 attr1="2"/>
            </model3>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=[TestSubModel(__root__=1), TestSubModel(__root__=2)])

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_submodel_extraction():
    class TestSubModel(BaseXmlModel, tag='model4'):
        attr1: int = attr()

    class TestModel(BaseXmlModel, tag='model1'):
        data: TestSubModel = wrapped('model2/model3', element())
        empty: Optional[TestSubModel] = wrapped('model2/model4', element())

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


def test_wrapped_mapping_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        attrs: Dict[str, str] = wrapped('model2/model3')

    xml = '''
    <model1>
        <model2>
            <model3 attr1="1" attr2="2"/>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(attrs={'attr1': 1, 'attr2': 2})

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_collection_extraction():
    class TestModel(BaseXmlModel, tag='model1'):
        elements: List[int] = wrapped('model2/model3', element(tag='model4'))

    xml = '''
    <model1>
        <model2>
            <model3>
                <model4>1</model4>
                <model4>2</model4>
                <model4>3</model4>
            </model3>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=[1, 2, 3])

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapper_sequence():
    class TestModel(BaseXmlModel, tag='model1'):
        element1: int = wrapped('model2')
        element2: int = wrapped('model3')
        element3: int = wrapped('model4')

    xml = '''
    <model1>
        <model2>1</model2>
        <model3>2</model3>
        <model4>3</model4>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(element1=1, element2=2, element3=3)

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapper_element_interleaving():
    class TestModel(BaseXmlModel, tag='model1'):
        element1: int = element(tag='element1')
        element2: int = wrapped('model2')
        element3: int = wrapped('model3')
        element4: int = element(tag='element4')
        element5: int = wrapped('model5')
        element6: int = element(tag='element6')

    xml = '''
    <model1>
        <element1>1</element1>
        <model2>2</model2>
        <model3>3</model3>
        <element4>4</element4>
        <model5>5</model5>
        <element6>6</element6>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        element1=1,
        element2=2,
        element3=3,
        element4=4,
        element5=5,
        element6=6,
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_wrapped_root():
    class TestSubModel(BaseXmlModel, tag='model3'):
        attr1: int = attr()

    class TestModel(BaseXmlModel, tag='model1'):
        __root__: TestSubModel = wrapped('model2')

    xml = '''
    <model1>
        <model2>
            <model3 attr1="1"/>
        </model2>
    </model1>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(__root__=TestSubModel(attr1=1))

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
