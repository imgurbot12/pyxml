"""
XPath Engine Unit Tests
"""
import unittest

from .. import fromstring

#** Variables **#
__all__ = ['XpathTests']

xml = fromstring(b"""
<document>
    <h1>Article Header</h1>
    <article class="message message-post">
        <span class="threadLabel ">(Thread Name #1)</span>
        <article class="message-body">
            <div class="message message-main">
                <p class="p1">Paragraph #1</p>
                <p>This is <em>Paragraph #2</em></p>
                <a href="https://example.com">Example Link</a>
                <p>Final Paragraph</p>
            </div>
        </article>
    </article>
    <article class="message message-post">
        <span class=" threadLabel">(Thread Name #2)</span>
        <article class="message-body">
            <div class="message message-main">
                <p class="p1">Paragraph #3</p>
                <a href="https://example.com">Example Link #2</a>
                <p>This is <em>Paragraph #4</em></p>
                <p>Final Paragraph Two</p>
            </div>
        </article>
    </article>
    <span class="footer">Footer Span</span>
</document>
""")

#** Classes **#

class XpathTests(unittest.TestCase):

    def assertTagCount(self, elements, tag, number):
        """assert that a certain number of children match the given tag"""
        matching = sum([1 for e in elements if e.tag == tag])
        self.assertEqual(matching, number, f'{tag!r} elements != {number}')

    def test_child(self):
        """test simple child iteration"""
        children = xml.findall('/*')
        self.assertEqual(len(children), 4)
        self.assertTagCount(children, 'h1', 1)
        self.assertTagCount(children, 'article', 2)
        self.assertTagCount(children, 'span', 1)

    def test_decendants(self):
        """test simple decendant iteration"""
        decendants = xml.findall('//*')
        self.assertTagCount(decendants, 'h1', 1)
        self.assertTagCount(decendants, 'article', 4)
        self.assertTagCount(decendants, 'span', 3)
        self.assertTagCount(decendants, 'div', 2)
        self.assertTagCount(decendants, 'p', 6)
        self.assertTagCount(decendants, 'a', 2)

    def test_tag_filter(self):
        """test simple tag filter"""
        articles = xml.findall('//article')
        self.assertEqual(len(articles), 4)
        self.assertTagCount(articles, 'article', 4)

    def test_tag_chain(self):
        """test simple tag filter chain"""
        spans = xml.findall('//article/span')
        self.assertEqual(len(spans), 2)
        self.assertTagCount(spans, 'span', 2)

    def test_relative_path(self):
        """test relative path filter"""
        spans = xml.findall('./article/span')
        self.assertEqual(len(spans), 2)
        self.assertTagCount(spans, 'span', 2)

    def test_index(self):
        """test simple xpath indexing"""
        headers = xml.findall('/[1]')
        self.assertEqual(len(headers), 1)
        self.assertTagCount(headers, 'h1', 1)

    def test_notempty(self):
        """test simple notempty variable check"""
        pgraphs = xml.findall('//p[@class]')
        self.assertEqual(len(pgraphs), 2)
        self.assertTagCount(pgraphs, 'p', 2)
        for p in pgraphs:
            self.assertIn('class', p.attrib)

    def test_name(self):
        """test `name` filter"""
        spans = xml.findall('//[name()="span"]')
        self.assertEqual(len(spans), 3)
        self.assertTagCount(spans, 'span', 3)

    def test_contains(self):
        """test `contains` filter"""
        threads = xml.findall('//span[contains(@class, "threadLabel")]')
        self.assertEqual(len(threads), 2)
        self.assertTagCount(threads, 'span', 2)

    def test_starts_with(self):
        """test `starts-with` filter"""
        threads = xml.findall('//span[starts-with(@class, "threadLabel")]')
        self.assertEqual(len(threads), 1)
        self.assertTagCount(threads, 'span', 1)

    def test_ends_with(self):
        """test `ends-with` filter"""
        threads = xml.findall('//span[ends-with(@class, "threadLabel")]')
        self.assertEqual(len(threads), 1)
        self.assertTagCount(threads, 'span', 1)

    def test_not(self):
        """test `not` filter"""
        spans = xml.findall('//span[not(ends-with(@class, "threadLabel"))]')
        self.assertEqual(len(spans), 2)
        self.assertTagCount(spans, 'span', 2)

    def test_get_text(self):
        """test `text()` value retrieval"""
        text = xml.findall('//h1/text()')
        self.assertEqual(len(text), 1)
        self.assertIsInstance(text[0], str)
        self.assertEqual(text[0].strip(), 'Article Header')

    def test_get_text_upper(self):
        """test `upper-case(text()) value retrieval`"""
        text = xml.findall('//h1/upper-case(text())')
        self.assertEqual(len(text), 1)
        self.assertIsInstance(text[0], str)
        self.assertEqual(text[0].strip(), 'ARTICLE HEADER')

    def test_get_attr(self):
        """test `@attribute` getter value retrieval"""
        classes = xml.findall('//span/@class')
        self.assertEqual(len(classes), 3)
        self.assertEqual(classes[0], 'threadLabel ')
        self.assertEqual(classes[1], ' threadLabel')
        self.assertEqual(classes[2], 'footer')

    def test_get_position(self):
        """test `position()` getter value retrieval"""
        pos = xml.findall('//span/position()')
        self.assertEqual(len(pos), 3)
        self.assertListEqual(pos, [0, 0, 3])

    def test_get_expr(self):
        """test arbitray expression getter value retrieval"""
        finals = xml.findall('//p/contains(upper-case(text()), "FINAL")')
        self.assertEqual(len(finals), 6)
        self.assertListEqual(finals, [False, False, True, False, False, True])

    def test_complex_child(self):
        """test complex child retrieval works as intended"""
        children = xml.findall('//article[@class="message-body"]/[1]/p[contains(text(), "Final")]')
        self.assertEqual(len(children), 2)
        self.assertTagCount(children, 'p', 2)

#** Init **#
if __name__ == '__main__':
    unittest.main()
