"""
XML Elements and ElementTree Implementation
"""
from typing import List, Optional, Iterator, Any
from typing_extensions import Self

#** Variables **#
__all__ = [
    'Element',
    'Comment',
    'ProcessingInstruction',
]

#** Functions **#

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

    def find(self, xpath: bytes) -> Optional[Self]:
        return xpathlib.find(self, xpath)

    def findall(self, xpath: bytes) -> List[Self]:
        return xpathlib.findall(self, xpath)

    def finditer(self, xpath: bytes) -> Iterator[Self]:
        return xpathlib.iterfind(self, xpath)

    def findtext(self, xpath: bytes, default=None) -> Optional[bytes]:
        return xpathlib.findtext(self, xpath, default)

class _Special(Element):
    """Baseclass for special elements such as Comments and PI"""

    def __init__(self, text: bytes):
        super().__init__(self.__class__.__name__.encode())
        self.text = text

    def itertext(self):
        return

class Comment(_Special):
    pass

class ProcessingInstruction(_Special):
    pass

#** Init **#
from . import xpath as xpathlib
