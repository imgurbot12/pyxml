"""
XML Parser Implementation Unit-Tests
"""
import unittest

from ..parser import Element, Parser, ParserError

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

edgecase_slashes = b"""
<document>
    <p class="abc">/</p>/
    <h1>/Content</h1>
</document>
"""

edgecase_style = b"""
<document>
    <head>
        <title>Title</title>
        <style>.main > .body { color: blue; }</style>
    </head>
</document>
"""

edgecase_script = b"""
<document>
    <h1>Script Below</h1>
    <script type="text/javascript" src="/test.js"></script>
    <script type="text/javascript">
        console.log("<<\\"<><>{}[]))");
    </script>
</document>
"""

edgecase_comment = b"""
<document>
    <head>Title</head><!---->
    <body>
        <div>Content!</div>
    </body>
</document>
"""

#** Functions **#

def text(e: Element) -> str:
    return e.text.strip() if e.text else ''

def tail(e: Element) -> str:
    return e.tail.strip() if e.tail else ''

#** Classes **#

class ParserTests(unittest.TestCase):
 
    def setUp(self) -> None:
        self.parser = Parser()

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
 
    def assertTree(self, xml: bytes, document: Element):
        """ensure trees are exactly as expected"""
        self.parser.feed(xml)
        root     = self.parser.close()
        parsed   = list(root.iter())
        expected = list(document.iter())
        self.assertEqual(len(parsed), len(expected))
        for p, e in zip(parsed, expected):
            self.assertEqual(p.tag, e.tag,   'tags do not match')
            self.assertEqual(text(p), text(e), f'{p.tag} text mismatch')
            self.assertEqual(tail(p), tail(e), f'{p.tag} tail mismatch')
            self.assertEqual(p.attrib, e.attrib, f'{p.tag} attrib mismatch')

    def test_broken_pi(self):
        """ensure proper exception for incomplete-pi"""
        self.parser.feed(incomplete_pi)
        self.assertRaises(ValueError, self.parser.close)

    def test_broken_start_tag(self):
        """ensure proper exception for broken start-tag"""
        self.parser.feed(incomplete_start_tag)
        self.assertParseError(self.parser.close, b'/p', (4, 43))

    def test_broken_end_tag(self):
        """ensure proper exception for broken start-tag"""
        self.parser.feed(incomplete_end_tag)
        self.assertParseError(self.parser.close, b'p', (5, 1))

    def test_unexpected_token(self):
        """ensure proper exception for unexpected token"""
        self.parser.feed(broken_xml)
        self.assertParseError(self.parser.close, b'', (1, 0))

    def test_edgecase_slashes(self):
        """ensure slashes edgecase does not raise errors"""
        self.assertTree(edgecase_slashes, 
            Element.new('document', children=[
                Element.new('p', {'class': 'abc'}, text='/', tail='/'),
                Element.new('h1', text='/Content'),
        ]))
    

    def test_edgecase_style(self):
        """ensure special styles tag edgecase does not raise errors"""
        self.assertTree(edgecase_style, 
            Element.new('document', children=[
                Element.new('head', children=[
                    Element.new('title', text='Title'),
                    Element.new('style', text='.main > .body { color: blue; }'),
            ])
        ]))

    def test_edgecase_script(self):
        """ensure special script tag edgecase does not raise errors"""
        self.assertTree(edgecase_script, 
            Element.new('document', children=[
                Element.new('h1', text='Script Below'),
                Element.new('script', {'type': 'text/javascript', 'src': '/test.js'}),
                Element.new('script', {'type': 'text/javascript'}, text='console.log("<<\\"<><>{}[]))");')
        ]))

    def test_edgecase_comment(self):
        """ensure special instaclose comment edgecase does not raise errors"""
        self.assertTree(edgecase_comment,
            Element.new('document', children=[
                Element.new('head', text='Title'),
                Element.new('body', children=[
                    Element.new('div', text='Content!')
                ])
            ])
        )
