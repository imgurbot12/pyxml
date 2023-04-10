"""
XML Xpath Query-Language Implementation
"""
from typing import Iterator, Optional, List

from .engine import iter_xpath, find_xpath, list_xpath
from ..element import Element

#** Variables **#
__all__ = ['iterfind', 'find', 'findall', 'findtext']

#** Functions **#

def iterfind(elem: Element, path: str, namespaces=None) -> Iterator[Element]:
    """
    iterate parse and evaluate xpath to find and filter elements

    :param elem: root element to search xpath from
    :param path: raw xpath expression
    :return:     iterator of elements matching xpath criteria
    """
    return iter_xpath(path.encode(), (e for e in (elem, )))

def find(elem: Element, path: str, namespaces=None) -> Optional[Element]:
    """
    find first matching element associated w/ xpath

    :param elem: root element to search xpath from
    :param path: raw xpath expression
    :return:     first element found matching criteria
    """
    return find_xpath(path.encode(), (e for e in (elem, )))

def findall(elem: Element, path: str, namespaces=None) -> List[Element]:
    """
    list parse and evaluate xpath to find and filter elements

    :param elem:  root element to search xpath from
    :param path:  raw xpath expression
    :return:      list of elements matching xpath criteria
    """
    return list_xpath(path.encode(), [elem])

def findtext(elem: Element, path: str, default=None, namespaces=None) -> Optional[str]:
    """
    retrieve text from first element match of xpath
    
    :param elem: root element to search xpath from
    :param path: raw xpath expression
    :return:     text from first element found matching criteria
    """
    match = find_xpath(path.encode(), (e for e in (elem, ))) 
    if match is None:
        return default
    if not match.text:
        return ''
    return match.text

