from typing import Dict, List, Union

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class Event(BaseXmlModel):
    timestamp: float = attr()


class KeyboardEvent(Event, tag='keyboard'):
    type: str = attr()
    key: str = element()


class MouseEvent(Event, tag='mouse'):
    position: Dict[str, int] = element()


class Log(BaseXmlModel, tag='log'):
    events: List[Union[KeyboardEvent, MouseEvent]]
# [model-end]


# [xml-start]
xml_doc = '''
<log>
    <mouse timestamp="1674999183.5486422">
        <position x="234" y="345"/>
    </mouse>
    <keyboard timestamp="1674999184.227246"
              type="KEYDOWN">
        <key>CTRL</key>
    </keyboard>
    <keyboard timestamp="1674999185.6342669"
              type="KEYDOWN">
        <key>C</key>
    </keyboard>
    <mouse timestamp="1674999186.270716">
        <position x="236" y="211"/>
    </mouse>
</log>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "events": [
        {
            "timestamp": 1674999183.5486422,
            "position": {"x": 234, "y": 345}
        },
        {
            "timestamp": 1674999184.227246,
            "type": "KEYDOWN",
            "key": "CTRL"
        },
        {
            "timestamp": 1674999185.6342669,
            "type": "KEYDOWN",
            "key": "C"
        },
        {
            "timestamp": 1674999186.270716,
            "position": {"x": 236, "y": 211}
        }
    ]
}
'''  # [json-end]

log = Log.from_xml(xml_doc)
assert log == Log.model_validate_json(json_doc)
