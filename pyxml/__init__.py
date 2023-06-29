"""
XML ElementTree/Parsing Library Implementation
"""

#** Variables **#
__all__ = [
    'xpath',
    'compat',

    'prettify',
    'tostring',
    'fromstring', 
    'ElementTree', 

    'Element',
    'Comment',
    'Declaration',
    'ProcessingInstruction',

    'Parser',
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
