"""
XML Tree Builder Implementation
"""
from typing import Dict, List, Iterator, Type, Optional
from typing_extensions import Self

#** Variables **#

#** Classes **#

class Element:
    """XML Element Object Definition"""
 
    def __init__(self, tag: bytes, attrib: Dict[bytes, bytes] = {}, **extra):
        self.tag    = tag
        self.attrib = {**attrib, **extra}
        self.children: List[Self] = []
        self.text:     Optional[bytes] = None
        self.tail:     Optional[bytes] = None
    
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

class TreeBuilder:
    """Simple XML Tree Building Implementation"""

    def __init__(self):
        self.text:    List[bytes]       = []
        self.tree:    List[Element]     = []
        self.root:    Optional[Element] = None
        self.last:    Optional[Element] = None
        self.tail:    bool              = False
        self.factory: Type[Element]     = Element

    def _flush(self):
        """flush collected text to right position in tree"""
        if not self.data:
            return
        if self.last is None:
            self.text = []
            return
        text = b''.join(self.text)
        if self.tail:
            if self.last.tail:
                raise RuntimeError('Element tail already assigned')
            self.last.tail = text
        else:
            if self.last.text:
                raise RuntimeError('Element text already assigned')
            self.last.text = text
        self.text = []

    def start(self, tag: bytes, attrs: Dict[bytes, bytes]):
        """process start of a new tag and update tree"""
        self._flush()
        elem = self.factory(tag, attrs)
        if self.tree:
            self.tree[-1].append(elem)
        elif self.root is None:
            self.root = elem
        self.last = elem
        self.tail = False
        self.tree.append(elem)

    def end(self, tag: bytes):
        """process end of an existing tag and update tree"""
        self._flush()
        self.last = self.tree.pop()
        if self.last.tag != tag:
            raise RuntimeError(
                f'End Tag Mismatch (Expected {self.last.tag}, Got {tag})')
        self.tail = True

    def data(self, data: bytes):
        """process incoming text block"""
        self.text.append(data)

    def comment(self, comment: bytes):
        pass

    def declaration(self, declaration: bytes):
        pass

    def handle_pi(self, pi: bytes):
        pass
