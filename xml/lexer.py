"""
Xml Parser Lexer/Tokenizer
"""
from enum import IntEnum
from typing import Optional

from ._tokenize import *

# ** Variables **#
__all__ = ['Token', 'Lexer']

OPEN_TAG = ord('<')
CLOSE_TAG = ord('>')
EQUALS = ord('=')
BANG = ord('!')
DASH = ord('-')
QUESTION = ord('?')

SPECIAL = b'=<>'


# ** Classes **#

class Token(IntEnum):
    TAG_START = 1
    TAG_END = 2
    ATTR_NAME = 3
    ATTR_VALUE = 5
    TEXT = 6
    COMMENT = 7
    DECLARATION = 8
    INSTRUCTION = 9


class Lexer(BaseLexer):
    """
    Simple XML Lexer/Tokenizer
    """

    def read_byte(self) -> int | None:
        """
        read next byte from array
        """
        if not self.buffer:
            try:
                return next(self.stream)
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

    def read_word(self, value: bytearray, terminate: bytes = b''):
        """
        read buffer until a space is found or special terminators
        """
        return super().read_word(value, SPECIAL)

    def read_text(self, value: bytearray):
        """
        read buffer until text-block ends
        """
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char in (OPEN_TAG, CLOSE_TAG):
                self.unread(char)
                break
            value.append(char)

    def read_comment(self, value: bytearray):
        """
        read until end of comment tag
        """
        buffer = bytearray()
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char == DASH:
                buffer.append(char)
                continue
            if char == CLOSE_TAG:
                break
            if buffer:
                value.extend(buffer)
                buffer.clear()
            value.append(char)

    def read_delcaration(self, value: bytearray):
        """
        read declaration string
        """
        self.read_comment(value)

    def read_instruction(self, value: bytearray):
        """
        read processing instruction tag
        """
        question = True
        while True:
            char = self.read_byte()
            if char is None:
                break
            if char in QUOTES:
                self.read_quote(char, value)
                continue
            if char == QUESTION:
                question = True
                continue
            if question:
                if char == CLOSE_TAG:
                    return
                question = False
            value.append(char)
        raise ValueError('instruction never terminated')

    def _next(self) -> Optional[Result]:
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
            # handle multi-character token asssessments
            if token == Token.TAG_START:
                if char == BANG:
                    token = Token.DECLARATION
                    continue
                if char == QUESTION:
                    token = Token.INSTRUCTION
                    continue
            if token in (Token.DECLARATION, Token.COMMENT) \
                    and char == DASH and not value:
                token = Token.COMMENT
                continue
            # break if new token starts/ends
            if char in (OPEN_TAG, CLOSE_TAG):
                self.unread(char)
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
            if token == Token.COMMENT:
                self.read_comment(value)
                break
            if token == Token.DECLARATION:
                self.read_delcaration(value)
                break
            if token == Token.INSTRUCTION:
                self.read_instruction(value)
                break
            raise ValueError('invalid character?', token, chr(char))
        return Result(token, bytes(value))
