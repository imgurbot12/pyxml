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
                <p>Paragraph #1</p>
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
                <p>Paragraph #3</p>
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
 
    def assertTagCount(self, children, tag, number):
        """assert that a certain number of children match the given tag"""
        matching = [c for c in children if c.tag == tag]
        self.assertEqual(len(matching), number, f'{tag!r} elements != {number}')

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
    
    def test_index(self):
        """test simple xpath indexing"""
        headers = xml.findall('/[1]')
        self.assertEqual(len(headers), 1)
        self.assertTagCount(headers, 'h1', 1)

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

#** Init **#
if __name__ == '__main__':
    unittest.main()
