import datetime as dt
from typing import Generic, Optional, Tuple, TypeVar

from pydantic import HttpUrl

import pydantic_xml as pxml

xml = '''
<request service-name="api-gateway"
         request-id="27765d90-f3ef-426f-be9d-8da2b405b4a9"
         timestamp="2019-06-12T12:21:34.123+00:00">
    <auth type="basic">
        <user>gw</user>
        <password>secret</password>
    </auth>
    <payload type="rpc">
        <method>crete_event</method>
        <param name="timestamp">1660892066.1952798</param>
        <param name="user">admin</param>
        <param name="method">POST</param>
        <param name="resource">https://api-gateway.test.com/api/v1/users</param>
    </payload>
</request>
'''


class BasicAuth(pxml.BaseXmlModel):
    type: str = pxml.attr()
    user: str = pxml.element()
    password: str = pxml.element()


AuthType = TypeVar('AuthType')
PayloadType = TypeVar('PayloadType')


class Request(pxml.BaseGenericXmlModel, Generic[AuthType, PayloadType], tag='request'):
    service_name: str = pxml.attr(name='service-name')
    request_id: str = pxml.attr(name='request-id')
    timestamp: dt.datetime = pxml.attr()

    auth: Optional[AuthType]

    payload: PayloadType


ParamsType = TypeVar('ParamsType')
ParamType = TypeVar('ParamType')


class Rpc(pxml.BaseGenericXmlModel, Generic[ParamsType]):
    class Param(pxml.BaseGenericXmlModel, Generic[ParamType]):
        name: str = pxml.attr()
        value: ParamType

    method: str = pxml.element()
    params: ParamsType = pxml.element(tag='param')


request = Request[
    BasicAuth,
    Rpc[
        Tuple[
            Rpc.Param[float],
            Rpc.Param[str],
            Rpc.Param[str],
            Rpc.Param[HttpUrl],
        ]
    ],
].from_xml(xml)

print(request)
print(request.json(indent=4))
print(request.to_xml(pretty_print=True).decode())
