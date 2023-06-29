"""
HTML Parser Implementation (matching html.parser)
"""
from io import BytesIO
from typing import Dict

from ..parser import Parser
from ..builder import TreeBuilder
from ..element import Element
from ..escape import find_charrefs, find_entityrefs

#** Variables **#
__all__ = [
    'HTML_FULL',
    'HTML_EMPTY', 

    'BaseHTMLParser',
    'HTMLParser', 
    'HTMLTreeParser'
]

#: list of elements to never shorten and always write full
HTML_FULL = {'style', 'script'}

#: list of empty html elements stolen from python stdlib
HTML_EMPTY = {"area", "base", "basefont", "br", "col", "embed", "frame", "hr",
              "img", "input", "isindex", "link", "meta", "param", "source",
              "track", "wbr"}

#** Classes **#

class TreeMiddleware(TreeBuilder):
    """custom middleware to bridge TreeBuilder w/ HTMLParser"""

    def __init__(self, parser: 'HTMLParser'):
        self.parser   = parser
        self.start    = parser.handle_startag
        self.end      = parser.handle_endtag
        self.startend = parser.handle_startendtag
        self.data     = parser.handle_data
        self.comment  = lambda text: parser.handle_comment(text)
        self.pi       = lambda target, pi: parser.handle_pi(f'{target} {pi}')
 
    def declaration(self, declaration: str):
        """process declaration according to type"""
        if declaration.lower().startswith('doctype'):
            self.parser.handle_decl(declaration)
            return
        self.parser.unknown_decl(declaration)

    def close(self):
        """no validation checks on finish by default"""
        pass

class BaseHTMLParser(Parser):

    def parse_tag(self, tag: str):
        """process tag w/ additional handling for empty tags"""
        super().parse_tag(tag, HTML_EMPTY)

class HTMLParser(BaseHTMLParser):

    def __init__(self, *, convert_charefs=True, fix_broken: bool = True):
        super().__post_init__(fix_broken)
        self.target          = TreeMiddleware(self)
        self.convert_charefs = convert_charefs
        self.reset()

    def unescape(self, value: str) -> str:
        """process and unescape reference values"""
        if self.convert_charefs:
            return super().unescape(value)
        # process charrefs / entityrefs
        for match in find_charrefs(value):
            self.handle_charref(match)
            value = value.replace(match, '')
        for match in find_entityrefs(value):
            self.handle_entityref(match)
            value = value.replace(match, '')
        return value 

    def reset(self):
        """reset parsing attributes to parse again"""
        self.lexer  = None
        self.buffer = BytesIO()

    def close(self) -> Element:
        """close parser and process data"""
        return super().close()

    def handle_startag(self, tag: str, attrs: Dict[str, str]):
        pass

    def handle_endtag(self, tag: str):
        pass

    def handle_startendtag(self, tag, attrs):
        self.handle_startag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str):
        pass
            
    def handle_entityref(self, name: str):
        pass

    def handle_charref(self, name: str):
        pass

    def handle_comment(self, name: str):
        pass

    def handle_decl(self, decl: str):
        pass

    def handle_pi(self, data: str):
        pass

    def unknown_decl(self, data: str):
        pass

class HTMLTreeParser(BaseHTMLParser):
    """HTML Parser Except it actually builds an Element-Tree by default"""
    pass
