"""
XPATH Processing Engine
"""
import re
from typing import *

from .lexer import XToken, XLexer, EToken, ELexer
from .functions import *
from ..element import Element
from .._tokenize import Result

#** Variables **#
__all__ = ['iter_xpath']

#: type hint for list of argument getters
Args = List[ArgGetter]

#: regex expression to match variable string
re_var = re.compile(r'^@\w+$')

#** Functions **#

def filter_tag(elements: List[Element], tag: str) -> List[Element]:
    """only return element if it matches the specified tag"""
    return [e for e in elements if e.tag == tag]

def get_parent(element: Element, parents: int) -> Optional[Element]:
    """retrieve parent elements from orignal element"""
    for _ in range(0, parents):
        if element.parent is None:
            return
        element = element.parent
    return element

def compile_expr(expr: bytes, pure: bool = True) -> Tuple[Args, Optional[Result], EvalExpr]:
    """compile a valid xpath filter expression"""
    # generate context for compiling expression
    lexer = ELexer(iter(expr))
    args: Args = []
    action: Optional[Result] = None
    compiled: EvalExpr = lambda _: False
    # modify action for special behaviors
    if expr.isdigit():
        action = Result(EToken.FUNCTION, b'index', 0, 0)
    if pure and re_var.match(expr.decode()):
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
            expr_args = compile_expr_args(value, pure)
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

def compile_expr_args(expr: bytes, pure: bool = True) -> Args:
    """compile a partial filter expression only to collect arguments"""
    args, action, _ = compile_expr(expr, pure)
    if action:
        raise ValueError('invalid arguments', action, args)
    return args 

def compile_expr_func(expr: bytes, pure: bool = True) -> EvalExpr:
    """compile a complete filter expression into a single function"""
    args, action, compiled = compile_expr(expr, pure)
    if action and args:
        raise ValueError('incomplete expression', action, args)
    return compiled

@overload
def iter_xpath(xpath: bytes, elems: Sequence[Element], pure: bool = True) -> Iterator[Element]:
    ...

@overload
def iter_xpath(xpath: bytes, elems: Sequence[Element], pure: bool = False) -> Iterator[Any]:
    ...

def iter_xpath(xpath: bytes, elems: Sequence[Element], pure: bool = False) -> Iterator[Any]:
    """
    iterate parse and evaluate xpath to find and filter elements

    :param xpath:    raw xpath expression
    :param elements: elements to search for xpath components
    :param pure:     avoid returning non-element values when true
    :return:         iterator of elements matching xpath criteria
    """
    lexer    = XLexer(iter(xpath))
    elements = list(elems)
    values   = None #type: Optional[List[Any]]
    for action in lexer.iter():
        # process action according to token-type
        token, value, _, _ = action
        if values:
            raise ValueError('cannot traverse elemtree after expression', value)
        elif token == XToken.CHILD:
            elements = [c for e in elements for c in e]
        elif token == XToken.DECENDANT:
            elements = [c for e in elements for c in e.iter()]
        elif token == XToken.NODE:
            elements = filter_tag(elements, value.decode())
        elif token in (XToken.WILDCARD, XToken.SELF):
            continue
        elif token == XToken.PARENT:
            parents  = (get_parent(e, len(value)) for e in elements)
            elements = [p for p in parents if p is not None]
        elif token == XToken.FILTER:
            expr     = compile_expr_func(value)
            elements = [e for e in elements if expr(e)]
        elif pure and token in (XToken.EXPRESSION, XToken.FUNCTION):
            raise ValueError(f'toplevel {token.name} disallowed', value)
        elif token == XToken.EXPRESSION:
            values             = elements if values is None else values
            args, action, func = compile_expr(value, False)
            # process as a getter if no action, else process like a function
            if action and func:
                values = [func(v) for v in values]
            elif not action:
                getter = args[0]
                values = [get_value(getter(v)) for v in values]
        elif token == XToken.FUNCTION:
            values = elements if values is None else values
            expr   = compile_expr_func(value)
            values = [expr(v) for v in values]
        else:
            raise ValueError('unsupported token', action)
    return iter(values or elements)
