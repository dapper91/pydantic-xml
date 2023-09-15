import datetime as dt
import ipaddress
import sys
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict
from uuid import UUID

import pytest
from helpers import assert_xml_equal
from pydantic import SerializerFunctionWrapHandler, ValidatorFunctionWrapHandler, field_serializer, field_validator
from pydantic import model_validator
from pydantic.functional_serializers import PlainSerializer, WrapSerializer
from pydantic.functional_validators import AfterValidator, BeforeValidator, WrapValidator

from pydantic_xml import BaseXmlModel, element


def test_primitive_types_encoding():
    class IntEnum(int, Enum):
        val1 = 1

    class StrEnum(str, Enum):
        val1 = '1'

    class TestModel(BaseXmlModel, tag='model'):
        field1: int = element(tag='field1')
        field2: float = element(tag='field2')
        field3: bool = element(tag='field3')
        field4: Decimal = element(tag='field4')
        field5: dt.datetime = element(tag='field5')
        field6: dt.date = element(tag='field6')
        field7: dt.time = element(tag='field7')
        field8: IntEnum = element(tag='field8')
        field9: StrEnum = element(tag='field9')
        field10: UUID = element(tag='field10')

    xml = '''
    <model>
        <field1>1</field1>
        <field2>1.1</field2>
        <field3>True</field3>
        <field4>3.14</field4>
        <field5>2023-02-04T12:01:02</field5>
        <field6>2023-02-04</field6>
        <field7>12:01:02</field7>
        <field8>1</field8>
        <field9>1</field9>
        <field10>acd3b2e3-7a3a-42fe-ba56-f7716bf7cae6</field10>
    </model>
    '''

    obj = TestModel(
        field1=1,
        field2=1.1,
        field3=True,
        field4=Decimal('3.14'),
        field5=dt.datetime(2023, 2, 4, hour=12, minute=1, second=2),
        field6=dt.date(2023, 2, 4),
        field7=dt.time(hour=12, minute=1, second=2),
        field8=1,
        field9='1',
        field10='acd3b2e3-7a3a-42fe-ba56-f7716bf7cae6',
    )

    actual_xml = obj.to_xml()
    assert_xml_equal(actual_xml, xml.encode())


def test_ipaddress_types_encoding():
    class TestModel(BaseXmlModel, tag='model'):
        ipv4address: ipaddress.IPv4Address = element()
        ipv6address: ipaddress.IPv6Address = element()
        ipv4network: ipaddress.IPv4Network = element()
        ipv6network: ipaddress.IPv6Network = element()
        ipv4interface: ipaddress.IPv4Interface = element()
        ipv6interface: ipaddress.IPv6Interface = element()

    xml = '''
    <model>
        <ipv4address>127.0.0.1</ipv4address>
        <ipv6address>::1</ipv6address>
        <ipv4network>198.51.100.0/24</ipv4network>
        <ipv6network>2001:db8::/32</ipv6network>
        <ipv4interface>198.51.100.42/24</ipv4interface>
        <ipv6interface>2001:db8::42/32</ipv6interface>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)
    expected_obj = TestModel(
        ipv4address=ipaddress.IPv4Address("127.0.0.1"),
        ipv6address=ipaddress.IPv6Address("::1"),
        ipv4network=ipaddress.IPv4Network("198.51.100.0/24"),
        ipv6network=ipaddress.IPv6Network("2001:db8::/32"),
        ipv4interface=ipaddress.IPv4Interface("198.51.100.42/24"),
        ipv6interface=ipaddress.IPv6Interface("2001:db8::42/32"),
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)


def test_field_serializer():
    class TestModel(BaseXmlModel, tag='model'):
        field1: dt.datetime = element(tag='field1')

        @field_serializer('field1')
        def serialize_dt(self, value: dt.datetime) -> float:
            return value.timestamp()

    xml = '''
    <model>
        <field1>1675468800.0</field1>
    </model>
    '''

    obj = TestModel(
        field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
    )

    actual_xml = obj.to_xml()
    assert_xml_equal(actual_xml, xml.encode())


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above")
@pytest.mark.parametrize(
    'Serializer', [
        PlainSerializer(lambda val: val.timestamp(), return_type=float),
        WrapSerializer(lambda val, nxt: val.timestamp(), return_type=float),
    ],
)
def test_serializer_annotations(Serializer: Any):
    from typing import Annotated

    Timestamp = Annotated[dt.datetime, Serializer]

    class TestSubModel(BaseXmlModel, tag='submodel'):
        field1: Timestamp = element(tag='field1')

    class TestModel(BaseXmlModel, tag='model'):
        field1: Timestamp = element(tag='field1')
        field2: TestSubModel

    xml = '''
    <model>
        <field1>1675468800.0</field1>
        <submodel>
            <field1>1675468800.0</field1>
        </submodel>
    </model>
    '''

    obj = TestModel(
        field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        field2=TestSubModel(
            field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        ),
    )

    actual_xml = obj.to_xml()
    assert_xml_equal(actual_xml, xml.encode())


def test_serializer_methods():
    class TestModel(BaseXmlModel, tag='model'):
        field1: dt.datetime = element()
        field2: dt.datetime = element()

        @field_serializer('field1', mode='plain')
        def serialize_field1(self, value: dt.datetime) -> float:
            return value.timestamp()

        @field_serializer('field2', mode='wrap')
        def serialize_field2(self, value: dt.datetime, nxt: SerializerFunctionWrapHandler) -> float:
            return nxt(value.timestamp())

    xml = '''
    <model>
        <field1>1675468800.0</field1>
        <field2>1675468800.0</field2>
    </model>
    '''

    obj = TestModel(
        field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        field2=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
    )

    actual_xml = obj.to_xml()
    assert_xml_equal(actual_xml, xml.encode())


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above")
@pytest.mark.parametrize(
    'Validator', [
        AfterValidator(lambda val: val.replace(tzinfo=dt.timezone.utc)),
        BeforeValidator(lambda val: dt.datetime.fromisoformat(val).replace(tzinfo=dt.timezone.utc)),
        WrapValidator(lambda val, hdr: hdr(dt.datetime.fromisoformat(val).replace(tzinfo=dt.timezone.utc))),
    ],
)
def test_validator_annotations(Validator: Any):
    from typing import Annotated

    DatetimeUTC = Annotated[dt.datetime, Validator]

    class TestSubModel(BaseXmlModel, tag='submodel'):
        field1: DatetimeUTC = element(tag='field1')

    class TestModel(BaseXmlModel, tag='model'):
        field1: DatetimeUTC = element(tag='field1')
        field2: TestSubModel

    xml = '''
    <model>
        <field1>2023-02-04T00:00:00</field1>
        <submodel>
            <field1>2023-02-04T00:00:00</field1>
        </submodel>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    expected_obj = TestModel.model_construct(
        field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        field2=TestSubModel.model_construct(
            field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        ),
    )

    assert actual_obj == expected_obj


def test_validator_methods():
    class TestModel(BaseXmlModel, tag='model'):
        field1: dt.datetime = element()
        field2: dt.datetime = element()
        field3: dt.datetime = element()

        @field_validator('field1', mode='wrap')
        def validate_field1(cls, value: str, handler: ValidatorFunctionWrapHandler) -> dt.datetime:
            return handler(dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc))

        @field_validator('field2', mode='before')
        def validate_field2(cls, value: str) -> dt.datetime:
            return dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc)

        @field_validator('field3', mode='after')
        def validate_field3(cls, value: dt.datetime) -> dt.datetime:
            return value.replace(tzinfo=dt.timezone.utc)

    xml = '''
    <model>
        <field1>2023-02-04T00:00:00</field1>
        <field2>2023-02-04T00:00:00</field2>
        <field3>2023-02-04T00:00:00</field3>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    expected_obj = TestModel.model_construct(
        field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        field2=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
        field3=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
    )

    assert actual_obj == expected_obj


def test_model_validator():
    class TestModel(BaseXmlModel, tag='model'):
        field1: dt.datetime = element()

        @model_validator(mode='before')
        def validate_model_before(cls, data: Dict[str, Any]) -> 'TestModel':
            return {
                'field1': dt.datetime.strptime(data['field1'], '%Y-%m-%d'),
            }

        @model_validator(mode='after')
        def validate_model_after(cls, obj: 'TestModel') -> 'TestModel':
            obj.field1 = obj.field1.replace(tzinfo=dt.timezone.utc)
            return obj

        @model_validator(mode='wrap')
        def validate_model_wrap(cls, obj: 'TestModel', handler: Callable) -> 'TestModel':
            return handler(obj)

    xml = '''
    <model>
        <field1>2023-02-04</field1>
    </model>
    '''

    actual_obj = TestModel.from_xml(xml)

    expected_obj = TestModel.model_construct(
        field1=dt.datetime(2023, 2, 4, tzinfo=dt.timezone.utc),
    )

    assert actual_obj == expected_obj
