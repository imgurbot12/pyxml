"""
XML Elements and ElementTree Implementation
"""
from typing import Dict, List, Optional, Iterator, Any
from typing_extensions import Self

# ** Variables **#
__all__ = [
    'Element',
    'Comment',
    'ProcessingInstruction',
]


# ** Functions **#

# ** Classes **#

class Element:
    """XML Element Object Definition"""

    def __init__(self, tag: bytes, attrib=None, **extra):
        if attrib is None:
            attrib = {}
        self.tag = tag
        self.attrib = {**attrib, **extra}
        self.children: List[Self] = []
        self.text: Optional[bytes] = None
        self.tail: Optional[bytes] = None

    def __repr__(self) -> str:
        return 'Element(tag=%r, attrib=%r)' % (self.tag, self.attrib)

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

    def extend(self, elements: Iterator[Self]):
        self.children.extend(elements)

    def remove(self, element: Self):
        self.children.remove(element)

    def clear(self):
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


class _Special(Element):
    """Baseclass for special elements such as Comments and PI"""

    def __init__(self, text: bytes):
        super().__init__(self.__class__.__name__.encode())
        self.text = text


class Comment(_Special):
    pass


class ProcessingInstruction(_Special):
    pass
