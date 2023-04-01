"""
Abstracted Python XML Parser Implementation
"""
from typing import Dict

from .lexer import Lexer

#** Classes **#

class Parser:
    
    def tag_start(self, tag: bytes, attrs: Dict[bytes, bytes]):
        """

        """
