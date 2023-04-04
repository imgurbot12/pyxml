"""
XPATH Processing Engine
"""
from typing import Iterator, List, Optional, Tuple

from .lexer import XToken, XLexer, EToken, ELexer
from .functions import *
from ..etree import Element
from .._tokenize import Result

#** Variables **#
__all__ = ['iter_xpath', 'find_xpath', 'list_xpath']

#: type hint for list of argument getters
Args = List[ArgGetter]

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

def compile_expr(expr: bytes) -> Tuple[Args, Optional[Result], EvalExpr]:
    """compile a valid xpath filter expression"""
    lexer = ELexer(stream(expr))
    args: Args = []
    action: Optional[Result] = None
    compiled: EvalExpr = lambda _: False
    while True:
        # retrieve next action in expression
        result = lexer.next()
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
            expr_args = compile_expr_args(value)
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

def compile_expr_args(expr: bytes) -> Args:
    """compile a partial filter expression only to collect arguments"""
    args, action, _ = compile_expr(expr)
    if action:
        raise ValueError('invalid arguments', action, args)
    return args 

def compile_expr_func(expr: bytes) -> EvalExpr:
    """compile a complete filter expression into a single function"""
    args, action, compiled = compile_expr(expr)
    if action and args:
        raise ValueError('incomplete expression', action, args)
    return compiled

def iter_xpath(xpath: bytes, elements: Iterator[Element]) -> Iterator[Element]:
    """
    iterate parse and evaluate xpath to find and filter elements

    :param xpath:    raw xpath expression
    :param elements: elements to search for xpath components
    :return:         iterator of elements matching xpath criteria
    """
    lexer = XLexer(stream(xpath))
    for action in lexer.iter():
        # process action according to token-type
        token, value = action
        if token == XToken.CHILD:
            elems = (c for e in elements for c in children(e))
        elif token == XToken.DECENDANT:
            elems = (c for e in elements for c in e.iter())
        elif token == XToken.NODE:
            elems = (e for e in filter_tag(elements, value))
        elif token == XToken.WILDCARD:
            continue
        elif token == XToken.FILTER:
            expr  = compile_expr_func(value)
            elems = (e for e in elements if expr(e))
        else:
            raise ValueError('unsupported token', action)
        elements = elems 
    return elements

def find_xpath(xpath: bytes, elements: Iterator[Element]) -> Optional[Element]:
    """
    find first matching element associated w/ xpath

    :param xpath:    raw xpath expression
    :param elements: elements to search for xpath components
    :return:         first element found matching criteria
    """
    try:
        return next(iter_xpath(xpath, elements))
    except StopIteration:
        return

def list_xpath(xpath: bytes, elements: List[Element]) -> List[Element]:
    """
    list parse and evaluate xpath to find and filter elements

    :param xpath:    raw xpath expression
    :param elements: elements to search for xpath components
    :return:         list of elements matching xpath criteria
    """
    return list(iter_xpath(xpath, (e for e in elements)))
