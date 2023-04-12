"""
Abstracted Python XML Parser Implementation
"""
import re
from io import BytesIO
from dataclasses import dataclass, field
from typing import List, Dict, BinaryIO, Iterator, Optional, Set, Tuple

from .lexer import DataStream, Token, Lexer, Result
from .builder import TreeBuilder
from .escape import unescape

#** Variables **#
__all__ = ['ParserError', 'Parser', 'FeedParser']

#: regex expression to retrieve encoding setting from xml pi
re_encoding = re.compile(r'encoding\s?=\s?([^\s,]+)', re.IGNORECASE)

#** Functions **#

def stream_file(f: BinaryIO, chunk_size: int = 8192) -> Iterator[int]:
    """stream bytes of file one at a time"""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield from chunk

#** Classes **#

class ParserError(SyntaxError):
    """error to raise on syntax error during parsing"""
    token:    Optional[int] = None
    code:     Optional[bytes] = None
    position: Optional[Tuple[int, int]] = None

    def __init__(self, msg: str, result: Optional[Result] = None):
        """generate parsing error w/ the following details"""
        error = msg
        if result is not None:
            pos    = (result.lineno, result.position)
            error += f' at {result.value.decode()!r}'
            error += ' lineno=%d, index=%d' % pos
            self.token    = result.token
            self.code     = result.value
            self.position = pos
        super().__init__(error)

@dataclass(repr=False)
class Parser:
    """
    A Very Simple XML Parser Implementation
    """
    stream:   DataStream
    builder:  TreeBuilder = field(default_factory=TreeBuilder)
    encoding: str         = 'utf-8'

    def __post_init__(self):
        self.lexer = Lexer(self.stream)

    def _decode(self, value: bytes) -> str:
        """decode value using appropriatly assigned encoding"""
        return value.decode(self.encoding)
    
    def unescape(self, value: str) -> str:
        """unescape the specified value if enabled"""
        return unescape(value)

    def parse_tag(self, tag: str, empty: Optional[Set[str]] = None):
        """
        iterate tokens from the lexer until single tag entry has been parsed
        """
        # if the tag is an end-tag skip further processing
        end = tag.startswith('/')
        if end:
            # ensure to read tag-end for ending slash
            result = self.lexer.next()
            if result is None or result.token != Token.TAG_END:
                raise ParserError('Missing Tag End', result)
            # process ending tag
            tag = tag.lstrip('/')
            self.builder.end(tag)
            return
        # process attributes on start-tag
        closed:     bool           = False
        incomplete: List[str]      = []
        attributes: Dict[str, str] = {}
        while True:
            result = self.lexer.next()
            if result is None or result.token == Token.TAG_END:
                break
            # process token value 
            token, value, _, _ = result
            value        = self._decode(value)
            # handle self-closed tags
            if token == Token.TAG_CLOSE:
                closed = True
                break
            # handle attribute tags
            elif token == Token.ATTR_NAME:
                incomplete.append(value)
                continue
            elif token == Token.ATTR_VALUE:
                attributes[incomplete.pop()] = self.unescape(value)
                continue
            raise ParserError('Unexpected Tag Token', result)
        # finalize processing for starting tag
        attributes.update({k:'true' for k in incomplete})
        if closed or (empty and tag in empty):
            if hasattr(self.builder, 'startend'):
                self.builder.startend(tag, attributes)
            else:
                self.builder.start(tag, attributes)
                self.builder.end(tag)
            return
        self.builder.start(tag, attributes)

    def process_pi(self, pi: str):
        """
        process pi-data and check for valid encoding
        """ 
        # process instruction to find specified encoding
        target, value = pi.split(' ', 1)
        if target == 'xml':
            for match in re_encoding.finditer(value):
                self.encoding = match.groups()[0].strip('\'"')
        self.builder.pi(target, value)

    def next(self) -> bool:
        """
        process a single xml object at a time, iterating the xml lexer
        """
        result = self.lexer.next()
        if result is None:
            return False
        # process value from result
        token, value, _, _ = result
        value        = self._decode(value)
        if token == Token.TAG_START:
            self.parse_tag(value)
        elif token == Token.TEXT:
            self.builder.data(self.unescape(value))
        elif token == Token.COMMENT:
            self.builder.comment(self.unescape(value))
        elif token == Token.DECLARATION:
            self.builder.declaration(value)
        elif token == Token.INSTRUCTION:
            self.process_pi(value)
        else:
            raise ParserError('Unexpected Next Token', result)
        return True

    def parse(self):
        """parse content until content is empty"""
        while self.next():
            pass
        return self.builder.close()

@dataclass(repr=False)
class FeedParser:
    target:   TreeBuilder = field(default_factory=TreeBuilder)
    encoding: str         = 'utf-8'

    def __post_init__(self):
        self.buffer = BytesIO()

    def feed(self, data: bytes):
        self.buffer.write(data)

    def close(self):
        self.buffer.seek(0)
        parser = Parser(stream_file(self.buffer), self.target, self.encoding)
        return parser.parse()
