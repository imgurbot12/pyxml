"""
Compatability Layer to replace `xml.etree.ElementTree`
"""
from ..etree import ElementTree, fromstring, tostring
from ..parser import Parser
from ..builder import TreeBuilder
from ..element import Element, Comment, ProcessingInstruction

#** Variables **#
__all__ = [
    'tostring',
    'fromstring',
    'Element',
    'Comment',
    'ProcessingInstruction',
    'ElementTree',
    'TreeBuilder',

    'XML',
    'PI',
    'XMLParser',
    'SubElement',
]

#: alias for fromstring func
XML = fromstring

#: alias for processing instruction
PI = ProcessingInstruction

#: expose feed-parser as XMLParser
XMLParser = Parser

#** Functions **#

def SubElement(parent, tag, attrib=None, **extra):
    """
    generate sub element of parent
    """
    attrib = {**(attrib or {}), **extra}
    element = parent.makeelement(tag, attrib)
    parent.append(element)
    return element
