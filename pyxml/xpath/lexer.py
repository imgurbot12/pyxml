"""
XPATH Search Syntax Lexer
"""
import string
from enum import IntEnum

from .._tokenize import *

#** Variables **#
__all__ = ['XToken', 'EToken', 'XLexer', 'ELexer']

SLASH = ord('/')
WILDCARD = ord('*')
OPEN_BRACK = ord('[')
CLOSE_BRACK = ord(']')
OPEN_PAREN = ord('(')
CLOSE_PAREN = ord(')')
ATSYM = ord('@')
COMMA = ord(',')
EQUALS = ord('=')
LESSTHAN = ord('<')
GREATERTHAN = ord('>')

AND   = b'and'
OR    = b'or'
TRUE  = b'true'
FALSE = b'false'

XSPECIAL = b'*[]/'
ESPECIAL = b'*[]()/<>,=.'

FUNC = b'()'

DIGIT = string.digits.encode()
WORD = string.ascii_letters.encode() + DIGIT + b'_'

#** Classes **#

class XToken(IntEnum):
    """XPath Tokens"""
    CHILD = 1
    DECENDANT = 2
    NODE = 3
    WILDCARD = 4
    FILTER = 5
    FUNCTION = 6


class EToken(IntEnum):
    """XPath Expression Tokens"""
    BOOLEAN = 1
    STRING = 2
    INTEGER = 3
    VARIABLE = 4
    COMMA = 5
    EXPRESSION = 6
    EQUALS = 7
    FUNCTION = 8
    LT = 9
    GT = 10
    LTE = 11
    GTE = 12
    AND = 13
    OR = 14

class XLexer(BaseLexer):
    """XPath Path Lexer"""

    def read_filter(self, value: bytearray):
        """
        read contents of filter until complete
        """
        while True:
            # break if empty or end of bracket
            char = self.read_byte()
            if char is None or char == CLOSE_BRACK:
                break
            # skip quotes
            if char in QUOTES:
                value.append(char)
                self.read_quote(char, value)
            value.append(char)

    def _next(self) -> Result:
        """parse basic xpath syntax (avoiding filter content)"""
        token = 0
        value = bytearray()
        while True:
            char = self.read_byte()
            if char is None:
                break
            # guess token based on first byte
            if not token:
                if char == SLASH:
                    value.append(char)
                    token = XToken.CHILD
                elif char == WILDCARD:
                    value.append(char)
                    token = XToken.WILDCARD
                    break
                elif char == OPEN_BRACK:
                    token = XToken.FILTER
                    self.read_filter(value)
                    break
                else:
                    token = XToken.NODE
                    value.append(char)
                    self.read_word(value, XSPECIAL)
                    break
                continue
            # handle parsing according to guessed token-type
            if token == XToken.CHILD:
                if char == SLASH:
                    token = XToken.DECENDANT
                    value.append(char)
                else:
                    self.unread(char)
                break
            raise ValueError('invalid character?', token, chr(char))
        # convert to function if ends with `()`
        if token != XToken.FILTER and value.endswith(FUNC):
            token = XToken.FUNCTION
        return Result(token, bytes(value))

class ELexer(BaseLexer):
    """XPath Logic and Function Expression Lexer"""

    def read_word(self, value: bytearray, terminate: bytes = b''):
        return super().read_word(value, terminate or ESPECIAL)

    def read_expression(self, value: bytearray):
        """
        read until the end of the function expression
        """
        parens = 1
        while True:
            char = self.read_byte()
            if char is None:
                break
            elif char in QUOTES:
                value.append(char)
                self.read_quote(char, value)
            elif char == OPEN_PAREN:
                parens += 1
            elif char == CLOSE_PAREN:
                parens -= 1
                if parens == 0:
                    break
            value.append(char)

    def guess_token(self, char: int, value: bytearray):
        """
        guess token type based on single character
        """
        if char == ATSYM:
            self.read_word(value)
            return EToken.VARIABLE
        if char == COMMA:
            return EToken.COMMA
        if char == EQUALS:
            return EToken.EQUALS
        if char == LESSTHAN:
            return EToken.LT
        if char == GREATERTHAN:
            return EToken.GT
        if char == OPEN_PAREN:
            self.read_expression(value)
            return EToken.EXPRESSION
        if char in DIGIT:
            value.append(char)
            self.read_word(value)
            return EToken.INTEGER
        if char in QUOTES:
            self.read_quote(char, value)
            return EToken.STRING
        value.append(char)
        return 0

    def _next(self) -> Result:
        token = 0
        value = bytearray()
        while True:
            char = self.read_byte()
            if char is None or char in SPACES:
                break
            # guess token based on first character
            if not token and not value:
                token = self.guess_token(char, value)
                if token and token <= EToken.EQUALS:
                    self.skip_spaces()
                    break
                continue
            # handle token parsing after guess
            if token in (EToken.LT, EToken.GT):
                if char == EQUALS:
                    token = EToken.LTE if token == EToken.LT else EToken.GTE
                else:
                    self.unread(char)
                self.skip_spaces()
                break
            # process function
            if char == OPEN_PAREN:
                token = EToken.FUNCTION
                self.unread(char)
                break
            value.append(char)
        # convert operator to valid token
        if not token:
            if value == AND:
                token = EToken.AND
            elif value == OR:
                token = EToken.OR
            elif value == TRUE:
                token = EToken.BOOLEAN
            elif value == FALSE:
                token = EToken.BOOLEAN
        return Result(token, bytes(value))
