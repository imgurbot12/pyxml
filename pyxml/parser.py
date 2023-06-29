"""
Abstracted Python XML Parser Implementation
"""
import os
import re
from abc import abstractmethod
from io import IOBase, BytesIO
from dataclasses import InitVar, dataclass, field
from typing import * #type: ignore
from typing import BinaryIO

from .lexer import DataStream, Token, Lexer, Result, BaseLexer
from .builder import TreeBuilder
from .element import Element
from .escape import unescape

#** Variables **#
__all__ = ['ParserError', 'BaseParser', 'Parser']

#: regex expression to retrieve encoding setting from xml pi
re_encoding = re.compile(r'encoding\s?=\s?([^\s,]+)', re.IGNORECASE)

#: environment controlled variable for lang behavior
FILE_CHUNK_SIZE = int(os.environ.get('PYXML_CHUNK_SIZE', '8192'))

#** Functions **#

def chunk_file(f, chunk_size: int = FILE_CHUNK_SIZE) -> Iterator[bytes]:
    """stream chunks of bytes from file"""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk

def stream_file(f, chunk_size: int = 8192) -> Iterator[int]:
    """stream bytes of file one at a time"""
    for chunk in chunk_file(f, chunk_size):
        yield from chunk

def write_parser(parser, data: Union[str, bytes, IOBase, BinaryIO]):
    """write a wide variety of content into parser"""
    if isinstance(data, (IOBase, BinaryIO)):
        if hasattr(parser, 'readfrom'):
            parser.readfrom(data)
            return
        for chunk in chunk_file(data):
            parser.feed(chunk)
        return
    data = data.encode() if isinstance(data, str) else data
    parser.feed(data)

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

class BaseParser(Protocol):
    target:   TreeBuilder
    stream:   Optional[DataStream]
    buffer:   Optional[IOBase]
    lexer:    Optional[Lexer]
    lfactory: Type[BaseLexer]
 
    def set_stream(self, stream: DataStream):
        """
        set parser stream directly

        :param stream: raw bytes data stream to parse into xml tree
        """
        if self.stream is not None:
            raise RuntimeError('data-stream already set')
        elif self.buffer is not None:
            raise RuntimeError('memory buffer already assigned')
        self.stream = stream

    def feed(self, data: bytes):
        """
        feed raw bytes into temporary buffer to parse

        :param data: raw bytes to add to internal read buffer
        """
        if self.stream is not None:
            raise RuntimeError('data-stream already provided')
        elif not self.buffer:
            self.buffer = BytesIO()
        elif not isinstance(self.buffer, BytesIO):
            raise RuntimeError('`readfrom` already called instead')
        self.buffer.write(data)

    def readfrom(self, file: IOBase):
        """
        replace memory buffer with file source
        
        :param file: file to replace internal read-buffer with
        """
        if self.stream is not None:
            raise RuntimeError('data-stream already provided')
        elif self.buffer:
            if not isinstance(self.buffer, BytesIO):
                raise RuntimeError('read buffer already replaced')
            elif self.buffer.tell() != 0:
                raise RuntimeError('memory buffer already in use')
        self.buffer = file
 
    @abstractmethod
    def next(self) -> bool:
        """
        process next element in internal lexer
        """
        raise NotImplementedError

    def close(self) -> Element:
        """
        stop consuming data from read buffer and parse existing content

        :return: element-tree root parsed from raw data
        """
        # assign stream based on internal state
        if self.stream is None:
            if self.buffer is None:
                raise RuntimeError('no data-stream provided')
            self.buffer.seek(0)
            self.stream = stream_file(self.buffer)
        # spawn lexer and complete parsing
        self.lexer = Lexer(self.stream)
        while self.next():
            pass
        return self.target.close()

@dataclass(repr=False)
class Parser(BaseParser):
    """
    A Very Simple XML Parser Implementation
    """
    target:     TreeBuilder             = field(default_factory=TreeBuilder)
    encoding:   str                     = 'utf-8'
    fix_broken: InitVar[Optional[bool]] = None

    def __post_init__(self, fix_broken: Optional[bool]):
        self.stream   = None
        self.buffer   = None
        self.lfactory = Lexer
        if fix_broken is not None:
            self.target.fix_broken = fix_broken

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
        # ensure lexer is assigned
        if self.lexer is None:
            raise RuntimeError('lexer nexver assigned')
        # if the tag is an end-tag skip further processing
        end = tag.startswith('/')
        if end:
            # ensure to read tag-end for ending slash
            result = self.lexer.next()
            if result is None or result.token != Token.TAG_END:
                raise ParserError('Missing Tag End', result)
            # process ending tag
            tag = tag.lstrip('/')
            self.target.end(tag)
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
            if hasattr(self.target, 'startend'):
                self.target.startend(tag, attributes)
            else:
                self.target.start(tag, attributes)
                self.target.end(tag)
            return
        self.target.start(tag, attributes)

    def process_pi(self, pi: str):
        """
        process pi-data and check for valid encoding
        """ 
        # process instruction to find specified encoding
        target, value = pi.split(' ', 1)
        if target == 'xml':
            for match in re_encoding.finditer(value):
                self.encoding = match.groups()[0].strip('\'"')
        self.target.pi(target, value)

    def next(self) -> bool:
        """
        process a single xml object at a time, iterating the xml lexer
        """
        # ensure lexer is assigned
        if self.lexer is None:
            raise RuntimeError('lexer nexver assigned')
        # retrieve next token to parse
        result = self.lexer.next()
        if result is None:
            return False
        # process value from result
        token, value, _, _ = result
        value        = self._decode(value)
        if token == Token.TAG_START:
            self.parse_tag(value)
        elif token == Token.TEXT:
            self.target.data(self.unescape(value))
        elif token == Token.COMMENT:
            self.target.comment(self.unescape(value))
        elif token == Token.DECLARATION:
            self.target.declaration(value)
        elif token == Token.INSTRUCTION:
            self.process_pi(value)
        else:
            raise ParserError('Unexpected Next Token', result)
        return True
