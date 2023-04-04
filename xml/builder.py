"""
XML Tree Builder Implementation
"""
from typing import Dict, List, Optional

from .etree import *

# ** Variables **#
__all__ = ['TreeBuilder']


# ** Classes **#

class TreeBuilder:
    """Simple XML Tree Building Implementation"""

    def __init__(self,
                 root: Optional[Element] = None,
                 element_factory = Element,
                 comment_factory = Comment,
                 pi_factory = ProcessingInstruction,
                 include_comments: bool = False,
                 include_pi: bool = False,
                 ):
        self.element_factory = element_factory
        self.comment_factory = comment_factory
        self.pi_factory = pi_factory
        self.include_comments = include_comments
        self.include_pi = include_pi
        self.root: Optional[Element] = root
        self.text: List[bytes] = []
        self.tree: List[Element] = []
        self.last: Optional[Element] = None
        self.tail: bool = False

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

    def _append(self, elem: Element):
        """append new element to the tree"""
        self.last = elem
        if self.tree:
            self.tree[-1].append(elem)
        elif self.root is None:
            self.root = elem

    def _inline(self, factory, *args):
        """generate single inline element and append it to the tree"""
        self._flush()
        elem = factory(*args)
        self._append(elem)
        self.tail = True

    def start(self, tag: bytes, attrs: Dict[bytes, bytes]):
        """process start of a new tag and update tree"""
        self._flush()
        elem = self.element_factory(tag, attrs)
        self._append(elem)
        self.tree.append(elem)
        self.tail = False

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
        """generate and include comment (if enabled)"""
        if self.include_comments:
            self._inline(self.comment_factory, comment)

    def declaration(self, declaration: bytes):
        pass

    def handle_pi(self, pi: bytes):
        """generate and include processing instruction (if enabled)"""
        if self.include_pi:
            self._inline(self.pi_factory, pi)
