from .element import XmlElementReader, XmlElementWriter

XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'


def is_element_nill(element: XmlElementReader) -> bool:
    if (is_nil := element.pop_attrib('{%s}nil' % XSI_NS)) and is_nil == 'true':
        return True
    else:
        return False


def make_element_nill(element: XmlElementWriter) -> None:
    element.set_attribute('{%s}nil' % XSI_NS, 'true')
