"""
XPath Expression/Filter Functions
"""
from functools import wraps
from typing import Callable, List, NamedTuple, Union

from .lexer import EToken
from ..element import Element
from .._tokenize import Result

#** Variables **#
__all__ = [
    'EvalExpr',
    'ArgValue',
    'ArgGetter',

    'wrap_expr',
    'compile_action',
    'compile_argument',
]

#: evaluation expression function
EvalExpr = Callable[[Element], Union[int, bool, bytes]]

#: argument value typehint
class ArgValue(NamedTuple):
    result: Result
    value:  bytes

#: argument getter function
ArgGetter = Callable[[Element], ArgValue]

#** Utilities **#

def wrap_expr(action: Result, expr: EvalExpr) -> ArgGetter:
    """wrap evaluate expression to act as an argument for later evaluation"""
    @wraps(expr)
    def expr_getter(e: Element) -> ArgValue:
        # run expression and convert type back to bytes
        raw = expr(e)
        if isinstance(raw, bool):
            value = b'true' if raw else b'false'
        elif isinstance(raw, int):
            value = str(raw).encode()
        elif isinstance(raw, bytes):
            value = raw
        else:
            raise ValueError('unexpected expression result', action, raw)
        # return valid argument value
        return ArgValue(action, value)
    return expr_getter

def compile_action(action: Result, args: List[ArgGetter]) -> EvalExpr:
    """build dynamic evaluation-expression given series of tokens"""
    # retrieve associated function
    func = BUILTIN.get(action.token)
    if action.token == EToken.FUNCTION and func is None:
        func = FUNCTIONS.get(action.value)
    if func is None:
        raise ValueError('unsupported func', action)
    # generate dynamic function
    @wraps(func)
    def wrapper(e: Element) -> bool:
        values = [getter(e) for getter in args]
        return func(e, *values)
    return wrapper

def compile_argument(arg: Result) -> ArgGetter:
    """compile argument collector function"""
    def getter(e: Element) -> ArgValue:
        # assign value
        if arg.token == EToken.VARIABLE:
            val = e.attrib.get(arg.value, b'')
        else:
            val = arg.value
        # assert value matches token and return arg-value
        if arg.token == EToken.INTEGER and not arg.value.isdigit():
            raise ValueError('invalid integer', arg)
        return ArgValue(arg, val)
    getter.__qualname__ = f'Getter[{arg.token!r},{arg.value!r}]'
    return getter

def get_int(arg: ArgValue) -> int:
    """retrieve integer value from argument-value"""
    if not arg.value.isdigit():
        raise ValueError('invalid integer', arg)
    return int(arg.value)

def get_bool(arg: ArgValue) -> bool:
    """retrieve boolean value from argument-value"""
    if arg.value not in (b'0', b'1', b'true', b'false'):
        raise ValueError('invalid boolean', arg)
    return arg.value in (b'1', b'true')

def get_value(arg: ArgValue) -> Union[bool, int, bytes]:
    """retrieve python value for arg-value"""
    if arg.result.token in (EToken.VARIABLE, EToken.STRING):
        return arg.value
    if arg.result.token == EToken.INTEGER:
        return get_int(arg)
    return arg.value == b'true'

#** Functions **#

def compare_eq(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """basic equal comparison"""
    return one.value == two.value

def compare_or(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """basic OR comparison"""
    return bool(get_value(one) or get_value(two))

def compare_and(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """baic AND comparison"""
    return bool(get_value(one) and get_value(two))

def compare_lt(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """basic LESS-THAN comparison"""
    return get_int(one) < get_int(two)

def compare_lte(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """basic LESS-THAN-EQUAL comparison"""
    return get_int(one) <= get_int(two)

def compare_gt(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """basic GREATER-THAN comparison"""
    return get_int(one) > get_int(two)

def compare_gte(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """basic GREATER-THAN-EQUAL comparison"""
    return get_int(one) >= get_int(two)

## Node Functions

def name(e: Element) -> bytes:
    """XPATH `name` function implementation"""
    return e.tag

def text(e: Element) -> bytes:
    """XPATH `text` function implementation"""
    text = bytearray(e.text or b'')
    for child in e.children:
        if child.tail:
            text += b' ' + child.tail
    return bytes(text)

def count(e: Element, tag: ArgValue) -> int:
    """XPATH `count` function implementation"""
    return sum(c.tag == tag.value for c in e.children)

def position(e: Element) -> int:
    """XPATH `position` function implementation"""
    if e.parent:
        for n, elem in enumerate(e.parent.children, 0):
            if elem == e:
                return n
    return 0

## Boolean Functions

def not_eq(_: Element, one: ArgValue) -> bool:
    """XPATH `not` function implementation"""
    return not get_bool(one)

## String Functions

def contains(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """XPATH `contains` function implentation"""
    return two.value in one.value

def starts_with(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """XPATH `starts-with` function implementation"""
    return one.value.startswith(two.value)

def ends_with(_: Element, one: ArgValue, two: ArgValue) -> bool:
    """XPATH `ends-with` function implementation"""
    return one.value.endswith(two.value)

def concat(_: Element, one: ArgValue, two: ArgValue) -> bytes:
    """XPATH `concat` function implementation"""
    return one.value + two.value

def substring(_: Element, b: ArgValue, s: ArgValue, e: ArgValue) -> bytes:
    """XPATH `substring` function implementation"""
    return b.value[get_int(s):get_int(e)]

def substring_before(_: Element, base: ArgValue, sub: ArgValue) -> bytes:
    """XPATH `substring-before` function implementation"""
    index = base.value.find(sub.value)
    index = index if index >= 0 else len(base.value)
    return base.value[:index]

def substring_after(_: Element, base: ArgValue, sub: ArgValue) -> bytes:
    """XPATH `substring-after` function implementation"""
    index = base.value.find(sub.value)
    index = index if index >= 0 else len(base.value)
    return base.value[index:]

def translate(_: Element, base: ArgValue, b: ArgValue, a: ArgValue) -> bytes:
    """XPATH `translate` fucntion implementation"""
    return base.value.replace(b.value, a.value)

def lower_case(_: Element, v: ArgValue) -> bytes:
    """XPATH `lower-case` function implementation"""
    return v.value.lower()

def upper_case(_: Element, v: ArgValue) -> bytes:
    """XPATH `upper-case` function implementation"""
    return v.value.upper()

## Axis Functions

def last(e: Element) -> bool:
    """XPATH `last` function implementation"""
    if e.parent:
        children = e.parent.children
        return children.index(e) == len(children) - 1
    return True

#** Init **#

#: map of etoken to associated expression function
BUILTIN = {
    EToken.EQUALS: compare_eq,
    EToken.OR:     compare_or,
    EToken.AND:    compare_and,
    EToken.LT:     compare_lt,
    EToken.LTE:    compare_lte,
    EToken.GT:     compare_gt,
    EToken.GTE:    compare_gte,
}

#: map of XPATH supported functions assigned by name
FUNCTIONS = {
    b'name':             name,
    b'text':             text,
    b'count':            count,
    b'position':         position,
    b'not':              not_eq,
    b'contains':         contains,
    b'starts-with':      starts_with,
    b'ends-with':        ends_with,
    b'substring':        substring,
    b'substring-before': substring_before,
    b'substring-after':  substring_after,
    b'translate':        translate,
    b'lower-case':       lower_case,
    b'upper-case':       upper_case,
    b'last':             last,
}
