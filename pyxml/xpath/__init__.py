"""
XML Xpath Query-Language Implementation
"""
from typing import Iterator, Optional, List, Any

from .engine import iter_xpath
from ..element import Element

#** Variables **#
__all__ = ['iterfind', 'find', 'findall', 'findtext']

#** Functions **#

def iterfind(elem: Element, path: str, namespaces=None) -> Iterator[Any]:
    """
    iterate parse and evaluate xpath to find and filter elements

    :param elem: root element to search xpath from
    :param path: raw xpath expression
    :return:     iterator of elements matching xpath criteria
    """
    return iter_xpath(path.encode(), (elem, ), False)

def find(elem: Element, path: str, namespaces=None) -> Optional[Any]:
    """
    find first matching element associated w/ xpath

    :param elem: root element to search xpath from
    :param path: raw xpath expression
    :return:     first element found matching criteria
    """
    try:
        return next(iterfind(elem, path, namespaces))
    except StopIteration:
        return

def findall(elem: Element, path: str, namespaces=None) -> List[Any]:
    """
    list parse and evaluate xpath to find and filter elements

    :param elem:  root element to search xpath from
    :param path:  raw xpath expression
    :return:      list of elements matching xpath criteria
    """
    return list(iterfind(elem, path, namespaces))

def findtext(elem: Element, path: str, default=None, namespaces=None) -> Optional[str]:
    """
    retrieve text from first element match of xpath
    
    :param elem: root element to search xpath from
    :param path: raw xpath expression
    :return:     text from first element found matching criteria
    """
    match = find(elem, path, namespaces)
    if match is None:
        return default
    if not match.text:
        return ''
    return match.text

