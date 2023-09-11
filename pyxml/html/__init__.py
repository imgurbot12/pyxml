"""
HTML Extensions to XML ElementTree Library
"""
from typing import Optional

from .parser import BaseHTMLParser, HTMLParser, HTMLTreeParser
from ..element import Element
from ..parser import BaseParser, write_parser
from ..etree import tostring as xml_tostring

#** Variables **#
__all__ = [
    'tostring', 
    'fromstring', 

    'HtmlElement',

    'BaseHTMLParser',
    'HTMLParser',
    'HTMLTreeParser',
]

#: compatability w/ lxml
HtmlElement = Element

#** Fuctions **#

def tostring(element: Element, **kwargs) -> bytes:
    """
    convert element to string w/ the given arguments

    :param element: element to convert to string
    :param kwargs:  keyword args to pass to serializer
    :return:        serialized bytes of element and children
    """
    kwargs.setdefault('method', 'html')
    return xml_tostring(element, **kwargs)

def fromstring(text, parser: Optional[BaseParser] = None,
    fix_broken: bool = True, **kwargs) -> Element:
    """
    convert raw xml bytes into valid element tree

    :param text:       xml text content to deserialize
    :param parser:     parser instance to process xml string
    :param fix_broken: ignore or attempt to repair broken xml
    :param kwargs:     kwargs to pass to parser implementation
    :return:           html element tree
    """
    parser = parser or HTMLTreeParser(fix_broken=fix_broken, **kwargs)
    write_parser(parser, text)
    return parser.close()
