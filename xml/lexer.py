"""
Xml Parser Lexer/Tokenizer
"""
from enum import IntEnum
from typing import NamedTuple

#** Variables **#
__all__ = ['Result', 'Lexer']

OPEN_TAG  = ord('<')
CLOSE_TAG = ord('>') 
EQUALS    = ord('=')

SPACES  = b'\n\r\t '
SPECIAL = b'=<>'
QUOTES  = b'"\''

#** Classes **#

# @tuple #type: ignore
class Result(NamedTuple):
    token: int
    value: bytes

class Token(IntEnum):
    TAG_START   = 1
    TAG_END     = 2
    ATTR_NAME   = 3
    ATTR_VALUE  = 5
    TEXT        = 6

class Lexer:
    """
    Simple XML Lexer/Tokenizer
    """

    def __init__(self, data: bytes):
        self.data       = iter(data)
        self.buffer     = bytearray()
        self.context    = bytearray()
        self.last_token = 0
    
    def read_byte(self) -> int | None:
        """
        read next byte from array
        """
        if not self.buffer:
            try:
                return next(self.data)
            except StopIteration:
                return
        return self.buffer.pop(0)
    
    def guess_token(self, char: int, value: bytearray) -> int:
        """
        guess the token-type based on a single character
        """
        # assume tag by a single character
        if char == OPEN_TAG:
            return Token.TAG_START
        if char == CLOSE_TAG:
            return Token.TAG_END
        if char == EQUALS:
            return Token.ATTR_VALUE
        # append value to context-aware tag types
        if self.last_token in (0, Token.TAG_END):
            value.append(char)
            return Token.TEXT
        if char not in SPACES:
            value.append(char)
            return Token.ATTR_NAME
        return 0
    
    def skip_spaces(self):
        """
        skip and ignore all whitespace until next text-block
        """
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char not in SPACES:
                self.buffer.append(char)
                break
    
    def read_word(self, value: bytearray):
        """
        read buffer until a space is found
        """
        while True:
            char = self.read_byte()
            if char is None or char in SPACES:
                break
            if char in SPECIAL:
                self.buffer.append(char)
                break
            value.append(char)

    def read_text(self, value: bytearray):
        """
        read buffer until text-block ends
        """
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char in (OPEN_TAG, CLOSE_TAG):
                self.buffer.append(char)
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
            escapes = (escapes + 1) if char == escapes else 0
            value.append(char)

    def next(self) -> Result | None:
        """
        parse the next token from the raw incoming data
        """
        token = 0
        value = bytearray()
        while True:
            # retrieve next character from session
            char = self.read_byte()
            if char is None:
                break
            # iterate until token-type can be determined
            if token == 0:
                token = self.guess_token(char, value)
                if token == Token.TAG_END:
                    break
                continue
            # break if new token starts/ends
            if char in (OPEN_TAG, CLOSE_TAG):
                self.buffer.append(char)
                break
            # append buffered character if not a quote
            if char not in QUOTES:
                value.append(char)
            # handle tag types separately
            if token in (Token.TAG_START, Token.ATTR_NAME):
                self.read_word(value)
                break
            if token == Token.ATTR_VALUE:
                self.skip_spaces()
                if char in QUOTES:
                    self.read_quote(char, value)
                else:
                    self.read_word(value)
                break
            if token == Token.TEXT:
                self.read_text(value)
                break
            raise ValueError('invalid character?', token, chr(char))
        # skip return if nothing was collected and data is empty
        if token == 0 and not value:
            return
        # track last token and return token result
        self.last_token = token
        return Result(token, value)
