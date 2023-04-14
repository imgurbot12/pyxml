"""
XPATH Processing Engine
"""
import re
from typing import Iterator, List, Optional, Tuple

from .lexer import XToken, XLexer, EToken, ELexer
from .functions import *
from ..element import Element
from .._tokenize import Result

#** Variables **#
__all__ = ['iter_xpath', 'find_xpath', 'list_xpath']

#: type hint for list of argument getters
Args = List[ArgGetter]

#: regex expression to match variable string
re_var = re.compile(r'^@\w+$')

#** Functions **#

def filter_tag(elements: Iterator[Element], tag: str) -> Iterator[Element]:
    """only return element if it matches the specified tag"""
    for elem in elements:
        if elem.tag == tag:
            yield elem

def get_parent(element: Element, parents: int) -> Optional[Element]:
    """retrieve parent elements from orignal element"""
    for _ in range(0, parents):
        if element.parent is None:
            return
        element = element.parent
    return element

def compile_expr(expr: bytes) -> Tuple[Args, Optional[Result], EvalExpr]:
    """compile a valid xpath filter expression"""
    # generate context for compiling expression
    lexer = ELexer(iter(expr))
    args: Args = []
    action: Optional[Result] = None
    compiled: EvalExpr = lambda _: False
    # modify action for special behaviors
    if expr.isdigit():
        action = Result(EToken.FUNCTION, b'index', 0, 0)
    if re_var.match(expr.decode()):
        action = Result(EToken.FUNCTION, b'notempty', 0, 0)
    # parse expression according to lexer bytes
    while True:
        # retrieve next action in expression
        result = lexer.next()
        if result is None:
            break
        # handle according to token
        token, value, _, _ = result
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
    lexer = XLexer(iter(xpath))
    for action in lexer.iter():
        # process action according to token-type
        token, value, _, _ = action
        if token == XToken.CHILD:
            elements = (c for e in elements for c in e)
        elif token == XToken.DECENDANT:
            elements = (c for e in elements for c in e.iter())
        elif token == XToken.NODE:
            elements = (e for e in filter_tag(elements, value.decode()))
        elif token in (XToken.WILDCARD, XToken.SELF):
            continue
        elif token == XToken.PARENT:
            parents  = (get_parent(e, len(value)) for e in elements)
            elements = (p for p in parents if p is not None)  
        elif token == XToken.FILTER:
            expr     = compile_expr_func(value)
            elements = (e for e in elements if expr(e))
        else:
            raise ValueError('unsupported token', action)
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
