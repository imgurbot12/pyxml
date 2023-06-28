"""
HTML Parser Tests
"""
import unittest

import requests

from .. import html

#** Variables **#
__all__ = ['HtmlTests']

#** Classes **#

class HtmlTests(unittest.TestCase):
    """HTML Parser Tests"""

    def parse_content(self, content: str):
        """parse, serialize, and reparse html content"""
        root  = html.fromstring(content, fix_broken=True)
        body  = html.tostring(root)
        root2 = html.fromstring(body)
        # ensure element-tags are the same
        tree  = [elem.tag for elem in root.iter()]
        tree2 = [elem.tag for elem in root2.iter()]
        self.assertEqual(tree, tree2)
        # ensure text is the same
        tree = [(elem.tag, elem.text, elem.tail) for elem in root.iter()]
        tree2 = [(elem.tag, elem.text, elem.tail) for elem in root2.iter()]
        self.assertEqual(tree, tree2)

    def parse_website(self, url: str):
        """download content from a website and test parser"""
        res = requests.get(url)
        self.parse_content(res.text)

    def test_example(self):
        """test example.com website"""
        self.parse_website('https://www.example.com')

    def test_google(self):
        """test google.com website"""
        self.parse_website('https://www.google.com')

    def test_foxnews(self):
        """test foxnews website"""
        self.parse_website('https://www.foxnews.com')

    def test_cnn(self):
        """test cnn website"""
        self.parse_website('https://cnn.com')

    def test_espn(self):
        """test espn"""
        self.parse_website('https://espn.com')
