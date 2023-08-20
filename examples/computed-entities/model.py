import pathlib
from ipaddress import IPv4Address
from typing import Dict, List
from xml.etree.ElementTree import canonicalize

from pydantic import Field, IPvAnyAddress, SecretStr, computed_field, field_validator

from pydantic_xml import BaseXmlModel, attr, computed_attr, computed_element


class Auth(BaseXmlModel, tag='Authorization'):
    type: str = attr(name='Type')
    value: SecretStr


class Request(BaseXmlModel, tag='Company'):
    forwarded_for: List[IPv4Address] = Field(exclude=True)
    raw_cookies: str = Field(exclude=True)
    raw_auth: str = Field(exclude=True)

    @field_validator('forwarded_for', mode='before')
    def validate_address_list(cls, value: str) -> List[IPv4Address]:
        return [IPvAnyAddress(addr) for addr in value.split(',')]

    @computed_attr(name='Client')
    def client(self) -> IPv4Address:
        client, *proxies = self.forwarded_for
        return IPvAnyAddress(client)

    @computed_element(tag='Proxy')
    def proxy(self) -> List[IPv4Address]:
        client, *proxies = self.forwarded_for
        return [IPvAnyAddress(addr) for addr in proxies]

    @computed_element(tag='Cookies')
    def cookies(self) -> Dict[str, str]:
        return dict(
            tuple(pair.split('=', maxsplit=1))
            for cookie in self.raw_cookies.split(';')
            if (pair := cookie.strip())
        )

    @computed_field
    def auth(self) -> Auth:
        auth_type, auth_value = self.raw_auth.split(maxsplit=1)
        return Auth(type=auth_type, value=auth_value)


request = Request(
    forwarded_for="203.0.113.195,150.172.238.178,150.172.230.21",
    raw_cookies="PHPSESSID=298zf09hf012fh2; csrftoken=u32t4o3tb3gg43;",
    raw_auth="Basic YWxhZGRpbjpvcGVuc2VzYW1l",
)

xml_doc = pathlib.Path('./doc.xml').read_text()
assert canonicalize(request.to_xml(), strip_text=True) == canonicalize(xml_doc, strip_text=True)
