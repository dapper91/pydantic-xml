from typing import List, Optional, Tuple

from pydantic_xml import BaseXmlModel, RootXmlModel, attr


# [model-start]
class Product(BaseXmlModel, tag='product'):
    status: str = attr()
    title: str


class Launch(RootXmlModel[int], tag='launched'):
    pass


class Products(RootXmlModel):
    root: List[Tuple[Product, Optional[Launch]]]
# [model-end]


# [xml-start]
xml_doc = '''
<Products>
    <product status="running">Several launch vehicles</product>
    <launched>2013</launched>
    <product status="running">Starlink</product>
    <launched>2019</launched>
    <product status="development">Starship</product>
</Products>
'''  # [xml-end]

# [json-start]
json_doc = '''
[
    [
        {
            "title": "Several launch vehicles",
            "status": "running"
        },
        2013
    ],
    [
        {
            "title": "Starlink",
            "status": "running"
        },
        2019
    ],
    [
        {
            "title": "Starship",
            "status": "development"
        },
        null
    ]
]
'''  # [json-end]

products = Products.from_xml(xml_doc)
assert products == Products.model_validate_json(json_doc)
