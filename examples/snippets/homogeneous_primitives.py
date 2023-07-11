from typing import List

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Company(BaseXmlModel):
    products: List[str] = element(tag='Product')
# [model-end]


# [xml-start]
xml_doc = '''
<Company>
    <Product>Several launch vehicles</Product>
    <Product>Starlink</Product>
    <Product>Starship</Product>
</Company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "products": [
        "Several launch vehicles",
        "Starlink",
        "Starship"
    ]
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
