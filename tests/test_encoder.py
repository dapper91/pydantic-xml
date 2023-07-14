import datetime as dt
import ipaddress
from decimal import Decimal
from enum import Enum

import pytest
from helpers import assert_xml_equal

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

    xml = '''
    <model>
        <field1>1</field1>
        <field2>1.1</field2>
        <field3>true</field3>
        <field4>3.14</field4>
        <field5>2023-02-04T12:01:02</field5>
        <field6>2023-02-04</field6>
        <field7>12:01:02</field7>
        <field8>1</field8>
        <field9>1</field9>
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


def test_model_level_xml_encoder():
    class TestSubModel(BaseXmlModel, tag='submodel'):
        field1: dt.datetime = element(tag='field1')

    class TestModel(BaseXmlModel, tag='model'):
        class Config:
            xml_encoders = {
                dt.datetime: lambda val: val.timestamp(),
            }

        field1: dt.datetime = element(tag='field1')
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


def test_model_xml_encoder_inheritance():
    class BaseTestModel(BaseXmlModel, tag='submodel'):
        class Config:
            xml_encoders = {
                dt.datetime: lambda val: val.timestamp(),
            }

    class TestModel(BaseTestModel, tag='model'):
        class Config:
            pass

        field1: dt.datetime = element(tag='field1')

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


def test_model_xml_encoder_inheritance_with_plain_model():
    class BasePlainModel:
        pass

    class BaseTestModel(BaseXmlModel, tag='submodel'):
        class Config:
            xml_encoders = {
                dt.datetime: lambda val: val.timestamp(),
            }

    class TestModel(BaseTestModel, BasePlainModel, tag='model'):
        class Config:
            pass

        field1: dt.datetime = element(tag='field1')

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


def test_xml_encoder_recursion_error():
    class TestModel(BaseXmlModel, tag='model'):
        class Config:
            xml_encoders = {
                dt.datetime: lambda val: val,
            }

        field1: dt.datetime = element(tag='field1')

    obj = TestModel(field1=dt.datetime(2023, 2, 4))

    with pytest.raises(ValueError) as e:
        obj.to_xml()

    assert e.value.args[0] == "Circular reference detected"


def test_encoder_type_not_xml_serializable():
    class TestModel(BaseXmlModel, tag='model'):
        class Config:
            arbitrary_types_allowed = True

        field1: complex = element(tag='field1')

    obj = TestModel(field1=complex(1, 2))

    with pytest.raises(TypeError) as e:
        obj.to_xml()

    assert e.value.args[0] == f"Object of type 'complex' is not XML serializable"
