from typing import List, Optional, Tuple

from pydantic_xml import RootXmlModel, element


# [model-start]
class Products(RootXmlModel):
    root: List[Tuple[str, Optional[int]]] = element(tag='info')
# [model-end]


# [xml-start]
xml_doc = '''
<Products>
    <info type="status">running</info>
    <info type="launched">2013</info>
    <info type="status">running</info>
    <info type="launched">2019</info>
    <info type="status">development</info>
    <info type="launched"></info>
</Products>
'''  # [xml-end]

# [json-start]
json_doc = '''
[
    [
        "running",
        2013
    ],
    [
        "running",
        2019
    ],
    [
        "development",
        null
    ]
]
'''  # [json-end]

products = Products.from_xml(xml_doc)
assert products == Products.model_validate_json(json_doc)
