from pydantic_xml import BaseXmlModel, attr


# [model-start]
class Company(
    BaseXmlModel,
    nsmap={'co': 'http://company.org/co'},
):
    trade_name: str = attr(name='trade-name', ns='co')
    type: str = attr(ns='co')
# [model-end]


# [xml-start]
xml_doc = '''
<Company co:trade-name="SpaceX"
         co:type="Private"
         xmlns:co="http://company.org/co"/>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "trade_name": "SpaceX",
    "type": "Private"
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
