"""
HTML Extensions to XML ElementTree Library
"""
from io import BytesIO
from typing import Optional

from .parser import HTMLTreeParser
from ..element import Element

#** Variables **#
__all__ = ['tostring', 'fromstring']

#** Fuctions **#

def tostring(element: Element, **kwargs) -> bytes:
    """
    convert element to string w/ the given arguments

    :param element: element to convert to string
    :param kwargs:  keyword args to pass to serializer
    :return:        serialized bytes of element and children
    """
    from ..etree import ElementTree
    kwargs.setdefault('method', 'html')
    data = BytesIO()
    ElementTree(element).write(data, **kwargs)
    return data.getvalue()

def fromstring(text, parser: Optional[HTMLTreeParser] = None) -> Element:
    """
    convert raw html bytes into valid element tree

    :param text:   xml text content to deserialize
    :param parser: parser instance to process xml string
    :return:       html element tree
    """
    text   = text.encode() if isinstance(text, str) else text
    parser = parser or HTMLTreeParser()
    parser.feed(text)
    return parser.close()
