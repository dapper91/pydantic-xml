import ipaddress

from helpers import assert_xml_equal

from pydantic_xml import BaseXmlModel, element


def test_ipaddress_fields_extraction():
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
        ipv6interface=ipaddress.IPv6Interface("2001:db8::42/32")
    )

    assert actual_obj == expected_obj

    actual_xml = actual_obj.to_xml()
    assert_xml_equal(actual_xml, xml)
