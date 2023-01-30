from pydantic_xml import BaseXmlModel, attr, element


# [model-start]
class CompanyInfo(BaseXmlModel):
    trade_name: str = attr(name='trade-name')
    website: str = element()

    ...  # data validation logic


class Company(BaseXmlModel, tag='company'):
    __root__: CompanyInfo

    ...  # business logic
# [model-end]


# [xml-start]
xml_doc = '''
<company trade-name="SpaceX">
    <website>https://www.spacex.com</website>
</company>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "trade_name": "SpaceX",
    "website": "https://www.spacex.com"
}
'''  # [json-end]

env = Company.from_xml(xml_doc)
assert env == Company.parse_raw(json_doc)
