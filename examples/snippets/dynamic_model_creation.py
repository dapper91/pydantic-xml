from pydantic_xml import attr, create_model

# [model-start]
Company = create_model(
    'Company',
    trade_name=(str, attr(name='trade-name')),
    type=(str, attr()),
)

# [model-end]


# [xml-start]
xml_doc = '''
<Company trade-name="SpaceX" type="Private"/>
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
