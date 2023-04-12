"""
XML ElementTree/Parsing Library Implementation
"""

#** Variables **#
__all__ = [
    'xpath',
    'compat',

    'tostring', 
    'fromstring', 
    'ElementTree', 

    'Element',
    'Comment',
    'Declaration',
    'ProcessingInstruction',

    'Parser',
    'FeedParser',
    'ParserError',

    'TreeBuilder',
    'BuilderError',
]

#** Imports **#
from .etree import *
from .element import *
from .parser import *
from .builder import *

from . import xpath
from . import compat
