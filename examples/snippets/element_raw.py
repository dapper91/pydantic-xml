from typing import List
from xml.etree.ElementTree import canonicalize

from pydantic import HttpUrl

from pydantic_xml import BaseXmlModel, computed_element, element
from pydantic_xml.element.native import ElementT as Element


# [model-start]
class Contact(BaseXmlModel, tag='contact'):
    url: HttpUrl


class Contacts(
    BaseXmlModel,
    tag='contacts',
    arbitrary_types_allowed=True,
):
    contacts_raw: List[Element] = element(tag='contact', exclude=True)

    @computed_element
    def parse_raw_contacts(self) -> List[Contact]:
        contacts: List[Contact] = []
        for contact_raw in self.contacts_raw:
            if url := contact_raw.attrib.get('url'):
                contact = Contact(url=url)
            elif (link := contact_raw.find('link')) is not None:
                contact = Contact(url=link.text)
            else:
                contact = Contact(url=contact_raw.text.strip())

            contacts.append(contact)

        return contacts
# [model-end]


# [xml-start-1]
src_doc = '''
<contacts>
    <contact url="https://www.linkedin.com/company/spacex" />
    <contact>
        <link>https://twitter.com/spacex</link>
    </contact>
    <contact>https://www.youtube.com/spacex</contact>
</contacts>
'''  # [xml-end-1]


contacts = Contacts.from_xml(src_doc)


# [xml-start-2]
dst_doc = '''
<contacts>
    <contact>https://www.linkedin.com/company/spacex</contact>
    <contact>https://twitter.com/spacex</contact>
    <contact>https://www.youtube.com/spacex</contact>
</contacts>
'''  # [xml-end-2]

assert canonicalize(contacts.to_xml(), strip_text=True) == canonicalize(dst_doc, strip_text=True)
