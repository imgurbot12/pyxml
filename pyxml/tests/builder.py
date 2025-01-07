"""
XML Builder Implementation Unit Tests
"""
import unittest
from typing import List

from ..builder import Element, TreeBuilder, BuilderError

#** Variables **#
__all__ = ['BuilderTests']

#** Classes **#

class BuilderTests(unittest.TestCase):

    def setUp(self) -> None:
        """setup builder for each test-case"""
        self.builder = TreeBuilder()

    def assertTags(self, root: Element, tags: List[str]):
        """assert iterated tags from root match expected"""
        elements = list(root.iter())
        self.assertEqual(len(elements), len(tags))
        for elem, tag in zip(elements, tags):
            self.assertEqual(elem.tag, tag)

    def test_multi_document(self):
        """ensure error on building multiple documents"""
        self.builder.start('document', {})
        self.builder.end('document')
        self.assertRaises(BuilderError, self.builder.start, 'document', {})

    def test_empty_document(self):
        """ensure error is raised if document is empty"""
        self.assertRaises(BuilderError, self.builder.close)

    def test_incomplete_document(self):
        """ensure error is raised on incomplete document"""
        self.builder.start('document', {})
        self.assertRaises(BuilderError, self.builder.close)

    def test_empty_tree(self):
        """ensure error is raised when ending on an empty tree"""
        self.builder.start('ul', {})
        self.builder.end('ul')
        self.assertRaises(BuilderError, self.builder.end, 'ul')

    def test_double_end(self):
        """ensure error is raised when a double ending is present"""
        self.builder.start('ul', {})
        self.builder.start('li', {})
        self.builder.end('li')
        self.assertRaises(BuilderError, self.builder.end, 'li')

    def test_fix_incomplete_inner(self):
        """ensure builder can fix incomplete inner-html"""
        self.builder.fix_broken = True
        self.builder.start('ul', {})
        self.builder.start('li-a', {})
        self.builder.end('li-a')
        self.builder.start('li-b', {})
        self.builder.start('a', {})
        self.builder.end('a')
        self.builder.end('ul')
        self.assertTags(self.builder.close(), ['ul', 'li-a', 'li-b', 'a'])

    def test_fix_incomplete_outer(self):
        """ensure builder can fix unclosed outer-html"""
        self.builder.fix_broken = True
        self.builder.start('html', {})
        self.builder.start('head', {})
        self.builder.start('title', {})
        self.builder.data('Title Page')
        self.builder.end('title')
        self.builder.start('style', {})
        self.builder.end('style')
        self.assertTags(self.builder.close(), ['html', 'head', 'title', 'style'])

    def test_fix_double_end(self):
        """ensure builder can fix double ending on untracked element"""
        self.builder.fix_broken = True
        self.builder.start('ul', {})
        self.builder.start('li', {})
        self.builder.end('li')
        self.builder.end('li')
        self.assertTags(self.builder.close(), ['ul', 'li'])
