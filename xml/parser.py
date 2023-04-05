"""
Abstracted Python XML Parser Implementation
"""
from typing import List, Dict

from .lexer2 import DataStream, Token, Lexer
from .builder import TreeBuilder

#** Variables **#
__all__ = ['Parser']

SLASH = b'/'
COLON = b':'
NS_PREFIX = b'xmlns'

#** Classes **#

class Parser:
    """
    A Very Simple XML Parser Implementation
    """

    def __init__(self, stream: DataStream, builder: TreeBuilder):
        """
        :param stream:  datastream of xml bytes to parse
        :param builder: builder factory used to build xml-tree
        """
        self.lexer = Lexer(stream)
        self.builder = builder

    def parse_tag(self, tag: bytes):
        """
        iterate tokens from the lexer until single tag entry has been parsed
        """
        # if the tag is an end-tag skip further processing
        end = tag.startswith(SLASH)
        if end:
            # ensure to read tag-end for ending slash
            result = self.lexer.next()
            if result is None or result.token != Token.TAG_END:
                raise RuntimeError('Missing Tag End', result)
            # process ending tag
            tag = tag.lstrip(SLASH)
            self.builder.end(tag)
            return
        # process attributes on start-tag
        closed:    bool = False
        incomplete: List[bytes] = []
        attributes: Dict[bytes, bytes] = {}
        while True:
            result = self.lexer.next()
            if result is None or result.token == Token.TAG_END:
                break
            # handle self-closed tags
            elif result.token == Token.TAG_CLOSE:
                closed = True
                break
            # handle attribute tags
            elif result.token == Token.ATTR_NAME:
                incomplete.append(result.value)
                continue
            elif result.token == Token.ATTR_VALUE:
                attributes[incomplete.pop()] = result.value
                continue
            raise RuntimeError('Unexpected Tag Token', result)
        # finalize processing for starting tag
        attributes.update({k: b'true' for k in incomplete})
        self.builder.start(tag, attributes)
        if closed:
            self.builder.end(tag)

    def next(self) -> bool:
        """
        process a single xml object at a time, iterating the xml lexer
        """
        result = self.lexer.next()
        if result is None:
            return False
        if result.token == Token.TAG_START:
            self.parse_tag(result.value)
        elif result.token == Token.TEXT:
            self.builder.data(result.value)
        elif result.token == Token.COMMENT:
            self.builder.comment(result.value)
        elif result.token == Token.DECLARATION:
            self.builder.declaration(result.value)
        elif result.token == Token.INSTRUCTION:
            self.builder.handle_pi(result.value)
        else:
            raise RuntimeError('Unexpected Next Token', result)
        return True

    def parse(self):
        """parse content until content is empty"""
        while self.next():
            pass
        return self.builder.root

