from typing import List

from pydantic import HttpUrl

from pydantic_xml import BaseXmlModel, element


# [model-start]
class Socials(BaseXmlModel, tag='socials'):
    __root__: List[HttpUrl] = element(tag='social')


class Contacts(BaseXmlModel, tag='contacts'):
    __root__: Socials
# [model-end]


# [xml-start]
xml_doc = '''
<contacts>
    <socials>
        <social>https://www.linkedin.com/company/spacex</social>
        <social>https://twitter.com/spacex</social>
        <social>https://www.youtube.com/spacex</social>
    </socials>
</contacts>
'''  # [xml-end]

# [json-start]
json_doc = '''
[
    "https://www.linkedin.com/company/spacex",
    "https://twitter.com/spacex",
    "https://www.youtube.com/spacex"
]
'''  # [json-end]

contacts = Contacts.from_xml(xml_doc)

assert contacts == Contacts.parse_raw(json_doc)
