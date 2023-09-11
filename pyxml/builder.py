"""
XML Tree Builder Implementation
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from .element import *

#** Variables **#
__all__ = ['BuilderError', 'TreeBuilder']

#** Classes **#

class BuilderError(SyntaxError):
    pass

@dataclass(repr=False)
class TreeBuilder:
    """Simple XML Tree Building Implementation"""
    root:            Optional[Element] = None
    element_factory: Type[Element]     = Element
    comment_factory: Type[Element]     = Comment
    declare_factory: Type[Element]     = Declaration
    pi_factory:      Type[Element]     = ProcessingInstruction
    insert_comments: bool              = False
    insert_declares: bool              = False
    insert_pis:      bool              = False
    fix_broken:      bool              = False
 
    def __post_init__(self):
        self.last:  Optional[Element] = self.root
        self.tree:  List[Element]     = [] if self.root is None else [self.root]
        self.text:  List[str]         = []
        self.tail:  bool              = False
        self.final: int               = 0 if self.root is None else 1

    def _flush(self):
        """flush collected text to right position in tree"""
        if not self.data:
            return
        if self.last is None:
            self.text = []
            return
        text = ''.join(self.text)
        if self.tail:
            if self.last.tail:
                if self.fix_broken:
                    self.last.tail += text
                    return
                raise BuilderError('Element tail already assigned')
            self.last.tail = text
        else:
            if self.last.text:
                if self.fix_broken:
                    self.last.text += text
                    return
                raise BuilderError('Element text already assigned')
            self.last.text = text
        self.text = []

    def _append(self, elem: Element):
        """append new element to the tree"""
        self.last = elem
        if self.tree:
            self.tree[-1].append(elem)
        elif self.root is None:
            self.root = elem
        elif self.fix_broken:
            # manually update root element to handle multi-document
            newroot = Element('document')
            newroot.text = '\n'
            newroot.append(self.root)
            self.root = newroot
            self.tree.insert(0, newroot)
            self.tree[-1].append(elem)
        else:
            raise BuilderError('more than one tree present')

    def _inline(self, factory, *args):
        """generate single inline element and append it to the tree"""
        self._flush()
        elem = factory(*args)
        self._append(elem)
        self.tail = True

    def start(self, tag: str, attrs: Dict[str, str]):
        """process start of a new tag and update tree"""
        self._flush()
        elem = self.element_factory(tag, attrs)
        self._append(elem)
        self.tree.append(elem)
        self.tail = False

    def end(self, tag: str):
        """process end of an existing tag and update tree"""
        # valdiate there is any content at all
        if not self.tree:
            if self.fix_broken:
                return
            raise BuilderError(f'Unexpected End. Tree Is Empty: {tag}')
        # validate tag ending matches tree
        self._flush()
        self.last = self.tree.pop()
        if self.last.tag != tag:
            if not self.fix_broken:
                raise BuilderError(
                    f'End Tag Mismatch (Expected {self.last.tag}, Got {tag})')
            # end whatever tag is missing manually before the last-tag
            if any(e.tag == tag for e in self.tree):
                return self.end(tag)
        self.tail = True
 
    def startend(self, tag: str, attrs: Dict[str, str]):
        """process self closing tags"""
        self.start(tag, attrs)
        self.end(tag)

    def data(self, data: str):
        """process incoming text block"""
        self.text.append(data)

    def comment(self, text: str):
        """generate and include comment (if enabled)"""
        if self.insert_comments:
            self._inline(self.comment_factory, text)

    def declaration(self, declaration: str):
        """generate and include declarations (if enabled)"""
        if self.root is not None and self.insert_declares:
            self._inline(self.declare_factory, declaration)

    def pi(self, target: str, pi: str):
        """generate and include processing instruction (if enabled)"""
        if self.insert_pis:
            self._inline(self.pi_factory, target, pi)

    def close(self):
        """close builder and return root element"""
        if len(self.tree) != self.final:
            if not self.fix_broken:
                raise BuilderError(
                    f'Missing End Tags {[e.tag for e in self.tree]}')
            # close all incomplete tags to avoid errors
            while len(self.tree) != self.final:
                self.end(self.tree[-1].tag)
        if self.root is None:
            raise BuilderError('Missing Toplevel Element')
        return self.root
