from typing import List, Union

import pydantic as pd

from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class VehicleTemplate(BaseXmlModel):
    drivers: int = attr()
    title: str = attr()
    engine: str = element()


class Car(VehicleTemplate, tag='car'):
    model_config = pd.ConfigDict(
        alias_generator=lambda field: {'title': 'make', 'engine': 'motor'}.get(field, field),
    )


class Airplane(VehicleTemplate, tag='airplane'):
    model_config = pd.ConfigDict(
        alias_generator=lambda field: {'drivers': 'pilots', 'title': 'model'}.get(field, field),
    )


class Vehicles(BaseXmlModel, tag='vehicles'):
    items: List[Union[Car, Airplane]]
# [model-end]


# [xml-start]
xml_doc = '''
<vehicles>
    <car make="Ford Mustang" drivers="1">
        <motor>Coyote V8</motor>
    </car>
    <airplane model="Bombardier Global 7500" pilots="2">
        <engine>General Electric Passport</engine>
    </airplane>
    <car make="Audi A8" drivers="1">
        <motor>V8</motor>
    </car>
</vehicles>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "items": [
        {
            "make": "Ford Mustang",
            "drivers": 1,
            "motor": "Coyote V8"
        },
        {
            "model": "Bombardier Global 7500",
            "pilots": 2,
            "engine": "General Electric Passport"
        },
        {
            "make": "Audi A8",
            "drivers": 1,
            "motor": "V8"
        }
    ]
}
'''  # [json-end]

vehicles = Vehicles.from_xml(xml_doc)
assert vehicles == Vehicles.model_validate_json(json_doc)
