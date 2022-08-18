import difflib
from typing import Union

import xmldiff.actions
import xmldiff.formatting
import xmldiff.main
from lxml import etree


def assert_xml_equal(
        left: Union[str, bytes],
        right: Union[str, bytes],
        *,
        ignore_comments: bool = True,
        pretty: bool = True,
        **kwargs,
):
    diffs = xmldiff.main.diff_texts(left, right, **kwargs)

    if ignore_comments:
        diffs = list(filter(lambda diff: not isinstance(diff, xmldiff.actions.InsertComment), diffs))

    if diffs:
        if pretty:
            parser = etree.XMLParser(remove_blank_text=True, remove_comments=ignore_comments)
            left = etree.tostring(etree.fromstring(left, parser=parser), pretty_print=True).decode()
            right = etree.tostring(etree.fromstring(right, parser=parser), pretty_print=True).decode()
            assert not diffs, '\n' + '\n'.join(difflib.Differ().compare(left.splitlines(), right.splitlines()))
        else:
            assert not diffs, '\n' + '\n'.join((str(diff) for diff in diffs))
