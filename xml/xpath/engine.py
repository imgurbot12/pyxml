"""
XPATH Processing Engine
"""
from itertools import chain
from typing import Iterator, List, Optional, Tuple

from .lexer import XToken, XLexer, EToken, ELexer
from .functions import *
from ..etree import Element
from .._tokenize import Result

#** Variables **#

#** Functions **#

def stream(data: bytes):
    """stream bytes from bytestring for lexer"""
    for byte in data:
        yield byte

def children(elem: Element) -> Iterator[Element]:
    """stream children attached to the specified element"""
    for child in elem:
        yield child

def filter_tag(elements: Iterator[Element], tag: bytes) -> Iterator[Element]:
    """only return element if it matches the specified tag"""
    for elem in elements:
        if elem.tag == tag:
            yield elem

#** Classes **#

class ExprEngine:

    def __init__(self, expr: bytes):
        self.lexer = ELexer(stream(expr))
 
    def next(self) -> Tuple[List[ArgGetter], Optional[Result], EvalExpr]:
        """
        parse expression and evaluate true/false
        """
        args: List[ArgGetter] = []
        action: Optional[Result] = None
        compiled: EvalExpr = lambda _: False
        while True:
            # retrieve next action in expression
            result = self.lexer.next()
            if result is None:
                break
            # handle according to token
            token, value = result
            if token >= EToken.EQUALS:
                action = result
                continue
            elif token <= EToken.VARIABLE:
                arg = compile_argument(result)
                args.append(arg)
            elif token == EToken.EXPRESSION:
                expr_args = ExprEngine(value).args()
                args.extend(expr_args)
            elif token == EToken.COMMA:
                pass
            else:
                raise ValueError('unsupported action?', result)
            # process action when specified
            if action:
                # compile expression function and reset args/action state
                compiled = compile_action(action, args)
                args     = [wrap_expr(action, compiled)]
                action   = None
        # ensure no args are left hanging
        return (args, action, compiled)
    
    def args(self) -> List[ArgGetter]:
        """compile expression into a series of arguments"""
        args, action, _ = self.next()
        if action:
            raise ValueError('invalid arguments', action, args)
        return args 

    def parse(self) -> EvalExpr:
        """compile expression given"""
        args, action, compiled = self.next()
        if action and args:
            raise ValueError('incomplete expression', action, args)
        return compiled

class XpathEngine:

    def __init__(self, xpath: bytes, elements: Iterator[Element]):
        self.lexer    = XLexer(stream(xpath))
        self.elements = elements

    def next(self) -> bool:
        """
        parse next section of xpath and search/filter specified elements
        """
        # retrieve how to process upcoming node
        action = self.lexer.next()
        if action is None:
            return False
        # process action according to token-type
        token, value = action
        if token == XToken.CHILD:
            print('get children')
            generators = [children(e) for e in self.elements]
        elif token == XToken.DECENDANT:
            print('get decendants')
            generators = [e.iter() for e in self.elements]
        elif token == XToken.NODE:
            print('filter', value)
            generators = [filter_tag(self.elements, value)]
        elif token == XToken.WILDCARD:
            print('wildcard', value)
            return True
        elif token == XToken.FILTER:
            print('filter', value)
            pass
        else:
            raise ValueError('unsupported token', action)
        self.elements = [e for gen in generators for e in gen]
        return True

    def parse(self) -> Iterator[Element]:
        """
        parse the specified xpath and return the finalized elements
        """
        while self.next():
            print([e.tag for e in self.elements])
            pass
        return self.elements

