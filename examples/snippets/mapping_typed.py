import datetime as dt

from pydantic import HttpUrl
from typing_extensions import TypedDict

from pydantic_xml import BaseXmlModel


# [model-start]
class Information(TypedDict):
    founded: dt.date
    employees: int
    website: HttpUrl


class Company(BaseXmlModel):
    info: Information
# [model-end]


# [xml-start]
xml_doc = '''
<Company founded="2002-03-14"
         employees="12000"
         website="https://www.spacex.com"/>
'''  # [xml-end]

# [json-start]
json_doc = '''
{
    "info": {
        "founded": "2002-03-14",
        "employees": 12000,
        "website": "https://www.spacex.com"
    }
}
'''  # [json-end]

company = Company.from_xml(xml_doc)
assert company == Company.model_validate_json(json_doc)
