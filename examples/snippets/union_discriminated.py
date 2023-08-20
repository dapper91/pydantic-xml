from typing import Literal, Union

from pydantic import Field

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class Device(BaseXmlModel, tag='device'):
    type: str


class CPU(Device):
    type: Literal['CPU'] = attr()
    cores: int = element()


class GPU(Device):
    type: Literal['GPU'] = attr()
    cores: int = element()
    cuda: bool = attr(default=False)


class Hardware(BaseXmlModel, tag='hardware'):
    accelerator: Union[CPU, GPU] = Field(..., discriminator='type')
# [model-end]


# [xml-start]
xml_doc = '''
<hardware>
    <device type="GPU">
        <cores>4096</cores>
    </device>
</hardware>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "accelerator": {
        "type": "GPU",
        "cores": 4096,
        "cuda": false
    }
}
'''  # [json-end]

hardware = Hardware.from_xml(xml_doc)
assert hardware == Hardware.model_validate_json(json_doc)
