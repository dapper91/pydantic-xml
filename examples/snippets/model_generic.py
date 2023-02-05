from typing import Generic, TypeVar
from uuid import UUID

from pydantic import SecretStr

from pydantic_xml import BaseGenericXmlModel, BaseXmlModel, attr, element

# [model-start]
AuthType = TypeVar('AuthType')


class Request(BaseGenericXmlModel, Generic[AuthType], tag='request'):
    request_id: UUID = attr(name='id')
    timestamp: float = attr()
    auth: AuthType


class BasicAuth(BaseXmlModel):
    user: str = attr()
    password: SecretStr = attr()


class TokenAuth(BaseXmlModel):
    token: UUID = element()


BasicRequest = Request[BasicAuth]
TokenRequest = Request[TokenAuth]
# [model-end]


# [xml-start]
xml_doc_1 = '''
<request id="27765d90-f3ef-426f-be9d-8da2b405b4a9"
         timestamp="1674976874.291046">
    <auth user="root" password="secret"/>
</request>
'''  # [xml-end]

# [json-start]
json_doc_1 = '''
{
    "request_id": "27765d90-f3ef-426f-be9d-8da2b405b4a9",
    "timestamp": 1674976874.291046,
    "auth": {
        "user": "root",
        "password": "secret"
    }
}
'''  # [json-end]

message = BasicRequest.from_xml(xml_doc_1)
assert message == BasicRequest.parse_raw(json_doc_1)

# [xml-start-2]
xml_doc_2 = '''
<request id="27765d90-f3ef-426f-be9d-8da2b405b4a9"
         timestamp="1674976874.291046">
    <auth>
        <token>7de9e375-84c1-441f-a628-dbaf5017e94f</token>
    </auth>
</request>
'''  # [xml-end-2]

# [json-start-2]
json_doc_2 = '''
{
    "request_id": "27765d90-f3ef-426f-be9d-8da2b405b4a9",
    "timestamp": 1674976874.291046,
    "auth": {
        "token": "7de9e375-84c1-441f-a628-dbaf5017e94f"
    }
}
'''  # [json-end-2]

message = TokenRequest.from_xml(xml_doc_2)
assert message == TokenRequest.parse_raw(json_doc_2)
