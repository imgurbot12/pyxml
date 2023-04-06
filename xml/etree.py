"""
XML Elements and ElementTree Implementation
"""
from ._compat import List, Optional, Iterator, Any, BinaryIO, Self


#** Variables **#
__all__ = [
    'Element',
    'Comment',
    'Declaration',
    'ProcessingInstruction',

    'ElementTree',
]

#: escape translations for cdata elements
ESCAPE_CDATA = {
    b'&': b'&amp;',
    b'<': b'&lt;',
    b'>': b'&gt;',
}

#: escape translations for attributes
ESCAPE_ATTRIB = {
    **ESCAPE_CDATA,
    b'"':  b'&quot;',
    b'\r': b'&#13;',
    b'\n': b'&#10;',
    b'\t': b'&#09;',
}

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

def escape_cdata(text: bytes) -> bytes:
    """escape special characters for text blocks"""
    for char, replace in ESCAPE_CDATA.items():
        if char in text:
            text = text.replace(char, replace)
    return text

def escape_attrib(text: bytes) -> bytes:
    """escape special characters for attributes"""
    for char, replace in ESCAPE_ATTRIB.items():
        if char in text:
            text = text.replace(char, replace)
    return text

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

class Element:
    """XML Element Object Definition"""

    def __init__(self, tag: bytes, attrib=None, **extra):
        if attrib is None:
            attrib = {}
        self.tag = tag
        self.attrib = {**attrib, **extra}
        self.parent:   Optional[Element] = None
        self.children: List[Self] = []
        self.text: Optional[bytes] = None
        self.tail: Optional[bytes] = None

    def __repr__(self) -> str:
        return 'Element(tag=%r, attrib=%r)' % (self.tag, self.attrib)
    
    def __iter__(self) -> Iterator[Self]:
        return (child for child in self.children)

    def __len__(self) -> int:
        return len(self.children)

    def __getitem__(self, index: int) -> Self:
        return self.children[index]

    def __setitem__(self, index: int, element: Self):
        self.children[index] = element

    def insert(self, index: int, element: Self):
        self.children.insert(index, element)

    def append(self, element: Self):
        self.children.append(element)
        element.parent = self

    def extend(self, elements: Iterator[Self]):
        self.children.extend(elements)
        for elem in elements:
            elem.parent = self

    def remove(self, element: Self):
        self.children.remove(element)
        element.parent = None

    def clear(self):
        for elem in self.children:
            elem.parent = None
        self.children.clear()

    def get(self, key: bytes, default: Any = None):
        return self.attrib.get(key, default)

    def set(self, key: bytes, value: bytes):
        self.attrib[key] = value

    def keys(self):
        return self.attrib.keys()

    def values(self):
        return self.attrib.values()

    def items(self):
        return self.attrib.items()

    def iter(self, tag: Optional[bytes] = None) -> Iterator[Self]:
        """iterate all children recursively from parent"""
        if tag is None or tag == self.tag:
            yield self
        for child in self.children:
            yield from child.iter(tag)
   
    def itertext(self):
        """iterate all elements with text in them and retreieve values"""
        if self.text:
            yield self.text
        for child in self.children:
            yield from child.itertext()

    def find(self, path: bytes) -> Optional[Self]:
        return xpathlib.find(self, path)

    def findall(self, path: bytes) -> List[Self]:
        return xpathlib.findall(self, path)

    def finditer(self, path: bytes) -> Iterator[Self]:
        return xpathlib.iterfind(self, path)

    def findtext(self, path: bytes, default=None) -> Optional[bytes]:
        return xpathlib.findtext(self, path, default)

class _Special(Element):
    """Baseclass for special elements such as Comments and PI"""

    def __init__(self, text: bytes):
        self._cname = self.__class__.__name__
        super().__init__(self._cname.encode())
        self.text = text
    
    def __repr__(self) -> str:
        return f'{self._cname}(text={self.text})'

    def itertext(self):
        return

class Comment(_Special):
    pass

class Declaration(_Special):
    pass

class ProcessingInstruction(_Special):
    pass

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
        

#** Init **#
from . import xpath as xpathlib
from .builder import TreeBuilder
from .parser import Parser
