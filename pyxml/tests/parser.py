"""
XML Parser Implementation Unit-Tests
"""
import unittest

from ..parser import Parser, ParserError

#** Variables **#
__all__ = ['ParserTests']

incomplete_pi = b"""
<document>
    <p>Paragraph #1</p>
    <?php echo "<p>Paragraph #2</p>"; >
    <p>Paragraph #3</p>
</document>
"""

incomplete_start_tag = b"""
<document>
    <p>Paragraph #1</p>
    <p class="this is a test" Paragraph #2</p>
    <p>Paragraph #3</p>
</document>
"""

incomplete_end_tag = b"""
<document>
    <p>Paragraph #1</p>
    <p class="this is a test"> Paragraph #2 </p
    <p>Paragraph #3</p>
</document>
"""

broken_xml = b"""
><document>
    <p>Paragraph #1</p>
    <p class="this is a test"> Paragraph #2 </p
    <p>Paragraph #3</p>
</document>
"""

#** Classes **#

class ParserTests(unittest.TestCase):

    def assertParseError(self, func, code, pos):
        """ensure parse error meets expectations"""
        # attempt to retrieve parse-error after calling func
        error = None
        try:
            func()
        except ParserError as e:
            error = e
        # process retrieval of error and do checks
        if error is None:
            self.fail('function did not raise expected error')
        self.assertEqual(error.code, code)
        self.assertEqual(error.position, pos)
    
    def test_broken_pi(self):
        """ensure proper exception for incomplete-pi"""
        parser = Parser(iter(incomplete_pi))
        self.assertRaises(ValueError, parser.parse)

    def test_broken_start_tag(self):
        """ensure proper exception for broken start-tag"""
        parser = Parser(iter(incomplete_start_tag))
        self.assertParseError(parser.parse, b'/p', (4, 43))

    def test_broken_end_tag(self):
        """ensure proper exception for broken start-tag"""
        parser = Parser(iter(incomplete_end_tag))
        self.assertParseError(parser.parse, b'p', (5, 1))

    def test_unexpected_token(self):
        """ensure proper exception for unexpected token"""
        parser = Parser(iter(broken_xml))
        self.assertParseError(parser.parse, b'', (1, 0))
