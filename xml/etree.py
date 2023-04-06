"""
XML Elements and ElementTree Implementation
"""

from ._compat import Optional, Iterator, BinaryIO

from .element import *
from .element import _Special
from .parser import Parser
from .builder import TreeBuilder
from .escape import escape_cdata, escape_attrib

#** Variables **#
__all__ = ['ElementTree']

TRUE  = b'true'
QUOTE = b'"'

#** Functions **#

def stream_file(f: BinaryIO, chunk_size: int = 8192) -> Iterator[int]:
    """stream bytes of file one at a time"""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield from chunk

def quote(text: bytes) -> bytes:
    """quote escape"""
    return QUOTE + text.replace(QUOTE, b'\\"') + QUOTE

def serialize_xml(f, element, short_empty_elements=False):
    """serialize xml and write into file"""
    # serialize special elements differently
    if isinstance(element, _Special):
        func = lambda b: b
        if isinstance(element, Comment):
            start, end, func = b'<!-- ', b'-->', escape_cdata
        elif isinstance(element, Declaration):
            start, end, func = b'<!', b'>', escape_cdata
        elif isinstance(element, ProcessingInstruction):
            start, end = b'<? ', b' ?>'
        else:
            raise RuntimeError('unsupported element', element)
        f.write(start + func(element.text or b'') + end)
        f.write(escape_cdata(element.tail or b''))
        return
    # serialize normal elements accordingly
    f.write(b'<' + element.tag)
    for name, value in element.attrib.items():
        f.write(b' ' + name)
        if value and value != TRUE:
            f.write(b'=')
            f.write(quote(escape_attrib(value)))
    # close w/ short form if enabled
    if short_empty_elements and not element.children and not element.text:
        f.write(b'/>')
        f.write(escape_cdata(element.tail or b''))
        return
    # close normally w/ children or otherwise disabled
    f.write(b'>')
    f.write(escape_cdata(element.text or b''))
    for child in element.children:
        serialize_xml(f, child, short_empty_elements)
    f.write(b'</' + element.tag + b'>')
    f.write(escape_cdata(element.tail or b''))

#** Classes **#

class ElementTree:

    def __init__(self, element=None, source=None):
        self.root: Optional[Element] = element
        if source:
            self.parse(source)

    def getroot(self) -> Element:
        if self.root is None:
            raise ValueError('No XML Root Element')
        return self.root

    def parse(self, source: BinaryIO, parser: Optional['Parser'] = None):
        parser    = parser or Parser(stream_file(source), TreeBuilder())
        self.root = parser.parse()

    def iter(self, tag=None):
        return self.getroot().iter(tag)

    def find(self, path: bytes):
        return self.getroot().find(path)

    def findall(self, path: bytes):
        return self.getroot().findall(path)
    
    def finditer(self, path: bytes):
        return self.getroot().finditer(path)

    def findtext(self, path: bytes):
        return self.getroot().findtext(path)

    def write(self, f: BinaryIO, short_empty_elements: bool = True):
        return serialize_xml(f, self.getroot(), short_empty_elements)
 
