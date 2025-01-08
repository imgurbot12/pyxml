"""
XML Element/Node Definitions
"""
from typing import Dict, Generator, Optional, List, Iterator, Any, Tuple
from typing_extensions import Self

#** Variables **#
__all__ = [
    'prettify',

    'Element',
    'Comment',
    'Declaration',
    'ProcessingInstruction',
]

#** Functions **#

def prettify(element: 'Element', indent: int = 2):
    """
    simple prettify function for xml elements

    :param element: element to prettify
    :param indent:  indent scale to use during evaluation
    """
    elements: List[Tuple[int, Element, bool]] = [(0, element, False)]
    while elements:
        level, elem, last = elements.pop(0)
        tail_level        = level if not last else (level - 1)
        next              = level + 1
        elem.text = (elem.text or '').strip()
        elem.tail = '\n' + ' ' * (tail_level * indent)
        if elem.children:
            elem.text = '\n' + ' ' * (next * indent) + elem.text
        for n, child in enumerate(elem.children, 1):
            elements.append((next, child, n == len(elem.children)))

#** Classes **#

class Element:
    """XML Element Object Definition"""
    __slots__ = ('tag', 'attrib', 'parent', 'children', 'text', 'tail')

    def __init__(self, tag, attrib=None, **extra):
        self.tag = tag
        self.attrib:   Dict[str, str]    = {**(attrib or {}), **extra}
        self.parent:   Optional[Element] = None
        self.children: List[Element]     = []
        self.text:     Optional[str]     = None
        self.tail:     Optional[str]     = None

    def __repr__(self) -> str:
        return 'Element(tag=%r, attrib=%r)' % (self.tag, self.attrib)

    def __iter__(self) -> Iterator['Element']:
        return iter(self.children)

    def __len__(self) -> int:
        return len(self.children)

    def __bool__(self):
        raise NotImplementedError

    def __getitem__(self, index: int) -> 'Element':
        return self.children[index]

    def __setitem__(self, index: int, element: 'Element'):
        self.children[index] = element

    @classmethod
    def makeelement(cls, tag, attrib) -> 'Element':
        """legacy support `makeelement` function"""
        return cls(tag, attrib)

    def insert(self, index: int, element: 'Element'):
        self.children.insert(index, element)

    def append(self, element: 'Element'):
        self.children.append(element)
        element.parent = self

    def extend(self, elements: Iterator['Element']):
        self.children.extend(elements)
        for elem in elements:
            elem.parent = self

    def remove(self, element: 'Element'):
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

    @classmethod
    def new(cls,
        tag:      str,
        attrib:   Optional[Dict[str, str]] = None,
        text:     Optional[str] = None,
        tail:     Optional[str] = None,
        children: Optional[List['Element']] = None,
    ) -> Self:
        """customizable secondary init-func for element"""
        element = cls(tag, attrib)
        element.text     = text
        element.tail     = tail
        element.children = children or []
        return element

    def prettify(self):
        """prettify self for self and children to have uniform spacing"""
        prettify(self)

    def iter(self, tag: Optional[bytes] = None) -> Iterator['Element']:
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

    def find(self, path: str) -> Optional[Any]:
        """retrieve single elmement matching xpath"""
        return xpath.find(self, path)

    def must_find(self, path: str) -> Any:
        """retrieve single element or item from xpath"""
        match = self.find(path)
        if match is None:
            raise KeyError(f'No Such Element At Xpath: {path!r}')
        return match

    def findall(self, path: str) -> List[Any]:
        """retrieve all elements in list matching xpath"""
        return xpath.findall(self, path)

    def finditer(self, path: str) -> Iterator[Any]:
        """iterate all elements matching xpath"""
        return xpath.iterfind(self, path)

    def findtext(self, path: str, default=None) -> Optional[str]:
        """collect all text within elements matching xpath"""
        return xpath.findtext(self, path, default)

    def xpath(self, path: str) -> List[Self]:
        """alias for findall for compatability with lxml"""
        return self.findall(path)

    def getparent(self) -> Optional['Element']:
        """retrieve parent for compatability with lxml"""
        return self.parent

    def getchildren(self) -> List['Element']:
        """retrieve children for compatability with lxml"""
        return self.children

class _Special(Element):
    """Baseclass for special elements such as Comments and PI"""

    def __init__(self, text: str):
        super().__init__(self.__class__)
        self.text   = text
        self._cname = self.__class__.__name__

    def __repr__(self) -> str:
        return f'{self._cname}(text={self.text})'

    def itertext(self) -> Generator[str, None, None]:
        yield from ()

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
