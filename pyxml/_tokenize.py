"""
BaseClass Tokenizer Implementation for various Lexers
"""
from typing import NamedTuple, Optional, Iterator, Generator

#** Variables **#
__all__ = ['SPACES', 'QUOTES', 'DataStream', 'Result', 'BaseLexer']

#: bytearray containing valid space characters
SPACES = b'\n\r\t '

#: bytearray containing valid quote characters
QUOTES = b'"\''

#: slash character byte
SLASH = ord('\\')

#: newline character byte
NEWLINE = ord('\n')

#: typehint for data stream of single bytes
DataStream = Iterator[int]

#** Classes **#

class Result(NamedTuple):
    token:    int
    value:    bytes
    lineno:   int
    position: int

class BaseLexer:
    """
    BaseClass Instance of Tokenizer Implementation
    """

    def __init__(self, stream: DataStream):
        self.stream = stream
        self.buffer = bytearray()
        self.last_token = 0
        self.lineno     = 1
        self.position   = 0

    def read_byte(self) -> Optional[int]:
        """
        read next byte from array
        """
        if not self.buffer:
            try:
                char = next(self.stream)
            except StopIteration:
                return
        else:
            char = self.buffer.pop(0)
        if char == NEWLINE:
            self.lineno  += 1
            self.position = 0
        self.position += 1
        return char

    def unread(self, *data):
        """
        unread bytes from the data-stream
        """
        self.position -= len(data)
        if NEWLINE in data or self.position < 0:
            raise RuntimeError('unable to track position!')
        self.buffer.extend(data)

    def skip_spaces(self):
        """
        skip and ignore all whitespace until next text-block
        """
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char not in SPACES:
                self.unread(char)
                break

    def read_word(self, value: bytearray, terminate: Optional[bytes] = None):
        """
        read buffer until a space is found or special terminators
        """
        while True:
            char = self.read_byte()
            if char is None or char in SPACES:
                break
            if terminate and char in terminate:
                self.unread(char)
                break
            value.append(char)

    def read_quote(self, quote: int, value: bytearray):
        """
        read quoted value
        """
        escapes = 0
        while True:
            char = self.read_byte()
            if char is None:
                break
            # check if quote is escaped
            if char == quote:
                if escapes % 2 == 0:
                    break
            # track escapes to know if quote is escaped or not
            escapes = (escapes + 1) if char == SLASH else 0
            value.append(char)

    def _next(self) -> Result:
        raise NotImplementedError

    def next(self) -> Optional[Result]:
        """
        parse the next token from the raw incoming data
        """
        result = self._next()
        # skip return if nothing was collected and data is empty
        if result.token == 0 and not result.value:
            return
        # track last token and return token result
        self.last_token = result.token
        return result

    def iter(self) -> Generator[Result, None, None]:
        """
        iterate token results parsed from lexer
        """
        while True:
            result = self.next()
            if result is None:
                break
            yield result
