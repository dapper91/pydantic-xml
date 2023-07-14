from typing import Dict, List, Tuple, Union

import pytest

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, errors, wrapped


@pytest.mark.parametrize(
    'model_name, element_tag',
    [
        ('field2', 'field2'),
        ('field1', None),
    ],
)
def test_element_tag_declaration_order(model_name, element_tag):
    class TestModel(BaseXmlModel, tag='model'):
        field1: str = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name}>value</{model_name}>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(field1="value")

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'expected_name, attribute_name',
    [
        ('attr2', 'attr2'),
        ('attr1', None),
    ],
)
def test_attribute_tag_declaration_order(expected_name, attribute_name):
    class TestModel(BaseXmlModel, tag='model'):
        attr1: str = attr(name=attribute_name)

    xml = '''
        <model {attribute_name}="attr1"/>
        '''.format(
        attribute_name=expected_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(attr1='attr1')

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, model_tag, element_tag',
    [
        ('model1', 'model1', None),
        ('model1', None, 'model1'),
        ('model1', 'model2', 'model1'),
        ('model2', None, None),
    ],
)
def test_submodel_tag_declaration_order(model_name, model_tag, element_tag):
    class TestSubModel(RootXmlModel, tag=model_tag):
        root: int

    class TestModel(BaseXmlModel, tag='model'):
        model2: TestSubModel = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name}>1</{model_name}>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model2=TestSubModel(1))

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, element_tag',
    [
        ('model2', 'model2'),
        ('model1', None),
    ],
)
def test_mapping_element_tag_declaration_order(model_name, element_tag):
    class TestModel(BaseXmlModel, tag='model'):
        model1: Dict[str, int] = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name} attr1="1" attr2="2"/>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model1={'attr1': 1, 'attr2': 2})

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, element_tag',
    [
        ('data', 'data'),
        ('elements', None),
    ],
)
def test_homogeneous_collection_element_tag_declaration_order(model_name, element_tag):
    class TestModel(BaseXmlModel, tag='model'):
        elements: List[int] = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name}>1</{model_name}>
        <{model_name}>2</{model_name}>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=[1, 2])

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, model_tag, element_tag',
    [
        ('model1', 'model1', None),
        ('model1', None, 'model1'),
        ('model1', 'model2', 'model1'),
        ('model2', None, None),
    ],
)
def test_submodel_homogeneous_collection_tag_declaration_order(model_name, model_tag, element_tag):
    class TestSubModel(RootXmlModel, tag=model_tag):
        root: int

    class TestModel(BaseXmlModel, tag='model'):
        model2: List[TestSubModel] = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name}>1</{model_name}>
        <{model_name}>2</{model_name}>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model2=[TestSubModel(1), TestSubModel(2)])

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, element_tag',
    [
        ('data', 'data'),
        ('elements', None),
    ],
)
def test_heterogeneous_collection_element_tag_declaration_order(model_name, element_tag):
    class TestModel(BaseXmlModel, tag='model'):
        elements: Tuple[int, int] = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name}>1</{model_name}>
        <{model_name}>2</{model_name}>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=(1, 2))

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, model_tag, element_tag',
    [
        ('model1', 'model1', None),
        ('model1', None, 'model1'),
        ('model1', 'model2', 'model1'),
        ('model2', None, None),
    ],
)
def test_submodel_heterogeneous_collection_tag_declaration_order(model_name, model_tag, element_tag):
    class TestSubModel(RootXmlModel, tag=model_tag):
        root: int

    class TestModel(BaseXmlModel, tag='model'):
        model2: Tuple[TestSubModel, TestSubModel] = element(tag=element_tag)

    xml = '''
    <model>
        <{model_name}>1</{model_name}>
        <{model_name}>2</{model_name}>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model2=(TestSubModel(1), TestSubModel(2)))

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, element_tag',
    [
        ('data', 'data'),
        ('elements', None),
    ],
)
def test_wrapped_element_tag_declaration_order(model_name, element_tag):
    class TestModel(BaseXmlModel, tag='model'):
        elements: int = wrapped('sub', element(tag=element_tag))

    xml = '''
    <model>
        <sub>
            <{model_name}>1</{model_name}>
        </sub>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(elements=1)

    assert actual_obj == expected_obj


@pytest.mark.parametrize(
    'model_name, model_tag, element_tag',
    [
        ('model1', 'model1', None),
        ('model1', None, 'model1'),
        ('model1', 'model2', 'model1'),
        ('model2', None, None),
    ],
)
def test_wrapped_model_element_tag_declaration_order(model_name, model_tag, element_tag):
    class TestSubModel(RootXmlModel, tag=model_tag):
        root: int

    class TestModel(BaseXmlModel, tag='model'):
        model2: TestSubModel = wrapped('sub', element(tag=element_tag))

    xml = '''
    <model>
        <sub>
            <{model_name}>1</{model_name}>
        </sub>
    </model>
    '''.format(
        model_name=model_name,
    )

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(model2=TestSubModel(1))

    assert actual_obj == expected_obj


def test_entity_name_not_provided_error():
    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: int = element()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: int = attr()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: List[int]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: Tuple[int, int]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: List[Dict[int, int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: Tuple[Dict[int, int], Dict[int, int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: List[Dict[int, int]]

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: Tuple[Dict[int, int], Dict[int, int]]


def test_wrapped_entity_name_not_provided_error():
    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: int = wrapped('sub', element())

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: int = wrapped('sub', attr())


def test_union_entity_name_not_provided_error():
    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: Union[int, str] = element()

    with pytest.raises(errors.ModelFieldError):
        class TestModel(RootXmlModel):
            root: Union[int, str] = attr()
