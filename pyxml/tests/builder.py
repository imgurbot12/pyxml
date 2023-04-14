"""
XML Builder Implementation Unit Tests
"""
import unittest

from ..builder import TreeBuilder, BuilderError

#** Variables **#
__all__ = ['BuilderTests']

#** Classes **#

class BuilderTests(unittest.TestCase):

    def setUp(self) -> None:
        """setup builder for each test-case"""
        self.builder = TreeBuilder()

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
