"""
HTML Parser Implementation (matching html.parser)
"""
from abc import ABC
from io import BytesIO
from typing import Optional, Dict, Optional

from ..lexer import Lexer
from ..parser import Parser, stream_file
from ..builder import TreeBuilder
from ..element import Element
from ..escape import find_charrefs, find_entityrefs

#** Variables **#
__all__ = ['HTML_EMPTY', 'HTMLParser', 'HTMLTreeParser']

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

class HTMLParser(Parser, ABC):

    def __init__(self, *, convert_charefs=True):
        self.buffer          = BytesIO()
        self.convert_charefs = convert_charefs

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
 
    def parse_tag(self, tag: str):
        """process tag w/ additional handling for empty tags"""
        super().parse_tag(tag, HTML_EMPTY)

    def reset(self):
        """reset parsing attributes to parse again"""
        self.lexer: Optional[Lexer] = None

    def feed(self, data: bytes):
        """write data into temporary buffer before parsing"""
        self.buffer.write(data)

    def close(self):
        """close parser and process data"""
        self.buffer.seek(0)
        self.lexer   = Lexer(stream_file(self.buffer))
        self.builder = TreeMiddleware(self)
        return self.parse()

    def handle_startag(self, tag: str, attrs: Dict[str, str]):
        print('start', tag, attrs)
        pass

    def handle_endtag(self, tag: str):
        print('end', tag)
        pass

    def handle_startendtag(self, tag, attrs):
        print('start-end', tag, attrs)
        self.handle_startag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str):
        print(f'data {data!r}')
        pass
            
    def handle_entityref(self, name: str):
        print(f'entityref {name!r}')
        pass

    def handle_charref(self, name: str):
        print(f'charref {name!r}')
        pass

    def handle_comment(self, name: str):
        print(f'comment {name!r}')
        pass

    def handle_decl(self, decl: str):
        print(f'decl {decl!r}')
        pass

    def handle_pi(self, data: str):
        print(f'pi {data!r}')
        pass

    def unknown_decl(self, data: str):
        print(f'unknown decl {data!r}')
        pass

class HTMLTreeParser(Parser):
    """HTML Parser Except it actually builds an Element-Tree by default"""
 
    def __init__(self, 
        builder:  Optional[TreeBuilder] = None, 
        encoding: str                   = 'utf-8'
    ):
        self.buffer   = BytesIO()
        self.builder  = builder or TreeBuilder(root=Element('document'))
        self.encoding = encoding
    
    def parse_tag(self, tag: str):
        """process tag w/ additional handling for empty tags"""
        super().parse_tag(tag, HTML_EMPTY)

    def feed(self, data: bytes):
        """write data into temporary buffer before parsing"""
        self.buffer.write(data)

    def close(self):
        """close parser and process data"""
        self.buffer.seek(0)
        self.lexer = Lexer(stream_file(self.buffer))
        return self.parse()

