import datetime as dt
from typing import List, Optional, Union

from pydantic_xml import BaseXmlModel, attr


# [model-start]
class Message(BaseXmlModel, tag='Message'):
    timestamp: Union[float, dt.datetime] = attr()
    text: Optional[str]


class Messages(BaseXmlModel):
    messages: List[Message]
# [model-end]


# [xml-start]
xml_doc_1 = '''
<Messages>
    <Message timestamp="1674995230.295639">hello world</Message>
    <Message timestamp="2023-01-29T17:30:38.762166"/>
</Messages>
'''  # [xml-end]

# [json-start]
json_doc_1 = '''
{
    "messages": [
        {
            "timestamp": 1674995230.295639,
            "text": "hello world"
        },
        {
            "timestamp": "2023-01-29T17:30:38.762166"
        }
    ]
}
'''  # [json-end]

messages = Messages.from_xml(xml_doc_1)
assert messages == Messages.parse_raw(json_doc_1)
