"""
XML Element/Node Definitions
"""
from typing import Dict, Optional, List, Iterator, Any
from typing_extensions import Self

#** Variables **#
__all__ = [
    'Element', 
    'Comment', 
    'Declaration',
    'ProcessingInstruction',
]

#** Classes **#

class Element:
    """XML Element Object Definition"""

    def __init__(self, tag, attrib=None, **extra):
        self.tag = tag
        self.attrib:   Dict[str, str]    = {**(attrib or {}), **extra}
        self.parent:   Optional[Element] = None
        self.children: List[Self]        = []
        self.text:     Optional[str]     = None
        self.tail:     Optional[str]     = None

    def __repr__(self) -> str:
        return 'Element(tag=%r, attrib=%r)' % (self.tag, self.attrib)
    
    def __iter__(self) -> Iterator[Self]:
        return iter(self.children)

    def __len__(self) -> int:
        return len(self.children)

    def __bool__(self):
        raise NotImplementedError

    def __getitem__(self, index: int) -> Self:
        return self.children[index]

    def __setitem__(self, index: int, element: Self):
        self.children[index] = element

    @classmethod
    def makeelement(cls, tag, attrib):
        return cls(tag, attrib)

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

    def get(self, key: str, default: Any = None):
        return self.attrib.get(key, default)

    def set(self, key: str, value: str):
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

    def find(self, path: str) -> Optional[Self]:
        return xpath.find(self, path)

    def findall(self, path: str) -> List[Self]:
        return xpath.findall(self, path)

    def finditer(self, path: str) -> Iterator[Self]:
        return xpath.iterfind(self, path)

    def findtext(self, path: str, default=None) -> Optional[str]:
        return xpath.findtext(self, path, default)

class _Special(Element):
    """Baseclass for special elements such as Comments and PI"""

    def __init__(self, text: str):
        super().__init__(self.__class__)
        self.text   = text
        self._cname = self.__class__.__name__
    
    def __repr__(self) -> str:
        return f'{self._cname}(text={self.text})'

    def itertext(self):
        return

class Comment(_Special):
    pass

class Declaration(_Special):
    pass

class ProcessingInstruction(_Special):
    
    def __init__(self, target: str, value: str):
        super().__init__(f'{target} {value}')
        self.target = target
        self.value  = value

#** Imports **#
from . import xpath
