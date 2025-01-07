"""
Xml Parser Lexer/Tokenizer
"""
from enum import IntEnum
from typing import Optional

from ._tokenize import *

#** Variables **#
__all__ = ['Token', 'Lexer']

OPEN_TAG    = ord('<')
CLOSE_TAG   = ord('>')
EQUALS      = ord('=')
BANG        = ord('!')
DASH        = ord('-')
QUESTION    = ord('?')
SLASH       = ord('/')
OPEN_BRACK  = ord('[')
CLOSE_BRACK = ord(']')

SPECIAL    = b'=<>/'
ONLY_SLASH = b'/'

SPECIAL_TAGS = {b'script', b'style'}

#** Classes **#

class Token(IntEnum):
    UNDEFINED   = 0
    TAG_START   = 1
    ATTR_NAME   = 2
    ATTR_VALUE  = 3
    TAG_END     = 4
    TAG_CLOSE   = 5
    COMMENT     = 6
    DECLARATION = 7
    INSTRUCTION = 8
    TEXT        = 9

class Lexer(BaseLexer):
    __slots__ = ('last_tag', 'fix_broken')

    def __init__(self, stream: DataStream, fix_broken=False):
        super().__init__(stream)
        self.last_tag: Optional[bytes] = None
        self.fix_broken = fix_broken

    def read_word(self, value: bytearray, terminate = None):
        """
        read buffer until space or a special XML character arises
        """
        while True:
            char = self.read_byte()
            if char is None or char in SPACES:
                break
            if char in SPECIAL:
                self.unread(char)
                break
            value.append(char)

    def read_tag(self, value: bytearray):
        """read buffer until a tag name is found"""
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char in SPACES:
                if value and value != ONLY_SLASH:
                    break
                continue
            if char in SPECIAL:
                self.unread(char)
                break
            value.append(char)

    def read_text(self, value: bytearray):
        """read buffer until text-block ends"""
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char in (OPEN_TAG, CLOSE_TAG):
                self.unread(char)
                break
            value.append(char)

    def read_special(self, value: bytearray, end: bytes):
        """read special style/script tag to completion"""
        buffer = bytearray()
        while True:
            char = self.read_byte()
            if char is None:
                break
            buffer.append(char)
            if buffer.endswith(end):
                value.extend(buffer[:-len(end)])
                self.unread(*end)
                break

    def read_comment(self, value: bytearray):
        """read until end of comment tag"""
        buffer = bytearray()
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char == DASH:
                if value:
                    buffer.append(char)
                continue
            if char == CLOSE_TAG and len(buffer) >= 2:
                break
            if buffer:
                value.extend(buffer)
                buffer.clear()
            value.append(char)
        #NOTE: remove initial - allowed into value buffer
        if value[0] == '-':
            value.pop(0)

    def read_delcaration(self, value: bytearray):
        """read declaration string"""
        brackets = 0
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char == OPEN_BRACK:
                brackets += 1
            elif char == CLOSE_BRACK:
                brackets -= 1
            elif char in QUOTES:
                value.append(char)
                self.read_quote(char, value)
            elif char == CLOSE_TAG and brackets <= 0:
                break
            value.append(char)

    def read_instruction(self, value: bytearray):
        """read processing instruction tag"""
        question = True
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char in QUOTES:
                value.append(char)
                self.read_quote(char, value)
            elif char == QUESTION:
                question = True
                continue
            elif question:
                if char == CLOSE_TAG:
                    return
                question = False
            value.append(char)
        raise ValueError('instruction never terminated')

    def look_ahead(self, find: int) -> bool:
        """look ahead in data-stream to see if char is present"""
        found  = False
        buffer = bytearray()
        while True:
            char = self.read_byte()
            if char is None:
                break
            buffer.append(char)
            if char in SPACES:
                continue
            elif char == find:
                found = True
            break
        if not found:
            self.buffer.extend(buffer)
        return found

    def guess_token(self, char: int, value: bytearray) -> int:
        """guess token based on a single character"""
        if char == OPEN_TAG:
            return Token.TAG_START
        elif char == SLASH and self.last_token != Token.TAG_END:
            if self.look_ahead(CLOSE_TAG):
                return Token.TAG_CLOSE
        elif char == CLOSE_TAG:
            return Token.TAG_END
        elif char == EQUALS and self.last_token == Token.ATTR_NAME:
            self.skip_spaces()
            return Token.ATTR_VALUE
        # parse according to additional context
        if not self.last_token or Token.TAG_END <= self.last_token <= Token.INSTRUCTION:
            value.append(char)
            return Token.TEXT
        elif char not in SPACES:
            value.append(char)
            return Token.ATTR_NAME
        return Token.UNDEFINED

    def handle_text(self, value: bytearray):
        """handle text parsing when value is text"""
        if self.last_tag in SPECIAL_TAGS:
            end_tag = f'</{self.last_tag.decode()}>'.encode()
            self.read_special(value, end_tag)
        else:
            self.read_text(value)

    def _next(self) -> Result:
        """parse the next token from the raw incoming data"""
        char     = 0
        token    = 0
        value    = bytearray()
        lineno   = self.lineno
        position = self.position
        while True:
            char = self.read_byte()
            if char is None:
                break
            # skip spaces if within tag definition
            if char in SPACES and self.last_token < Token.TAG_END:
                continue
            # guess token based on single character
            if not token:
                token = self.guess_token(char, value)
                if token in (Token.TAG_END, Token.TAG_CLOSE, Token.TEXT):
                    break
                continue
            # improve token guess for specific token-types
            if token == Token.TAG_START:
                if char == BANG:
                    token = Token.DECLARATION
                    continue
                if char == QUESTION:
                    token = Token.INSTRUCTION
                    continue
            if char == DASH and token == Token.DECLARATION:
                token = Token.COMMENT
                continue
            # append character save for certain exceptions
            if char not in QUOTES:
                value.append(char)
            # exit once token type is known
            if token:
                break
        # handle processing based on tag-type
        if token == Token.TAG_START:
            self.read_tag(value)
            # correct for invalid tags
            if all(c in SPECIAL for c in value) or value.startswith(b' '):
                token = Token.TEXT
                value.insert(0, OPEN_TAG)
                value.append(ord(' '))
                self.handle_text(value)
            else:
                self.last_tag = bytes(value)
        elif token == Token.ATTR_NAME:
            self.read_word(value)
            # correct for broken attributes
            if value and value[-1] == CLOSE_TAG:
                value = value[:-1]
                self.unread(CLOSE_TAG)
        elif token == Token.ATTR_VALUE:
            if char and char in QUOTES:
                self.read_quote(char, value)
            else:
                self.read_word(value)
        elif token in (Token.TAG_END, Token.TAG_CLOSE):
            pass
        elif token == Token.TEXT:
            self.handle_text(value)
        elif token == Token.COMMENT:
            self.read_comment(value)
        elif token == Token.DECLARATION:
            self.read_delcaration(value)
        elif token == Token.INSTRUCTION:
            self.read_instruction(value)
        elif char is not None:
            raise ValueError('invalid character?', token, chr(char))
        return Result(token, bytes(value), lineno, position)
