"""
Escape/Unescape Utilities for XML Handling
"""
import re
from typing import List

#** Variables **#
__all__ = [
    'find_charrefs', 
    'find_entityrefs', 
    'escape_cdata', 
    'escape_attrib', 
    'unescape'
]

#: find all charrefs
re_charref = re.compile(r'&#\w+;')

#: find all entityrefs
re_entityref = re.compile(r'&\w+;')

#: escape translations for cdata elements
ESCAPE_CDATA = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
}

#: escape translations for attributes
ESCAPE_ATTRIB = {
    **ESCAPE_CDATA,
    '"':  '&quot;',
    ' ':  '&nbsp;',
    '\r': '&#13;',
    '\n': '&#10;',
    '\t': '&#09;',
    '\'': '&#39;',
}

#: reverse dictionary used to unescape special characters
UNESCAPE_ATTRIB = {v:k for k,v in ESCAPE_ATTRIB.items()}

#** Functions **#

def find_charrefs(text: str) -> List[str]:
    """iterate all charrefs found in text"""
    return re_charref.findall(text)

def find_entityrefs(text: str) -> List[str]:
    """iterate all entityrefs found in text"""
    return re_entityref.findall(text)

def escape_cdata(text: str) -> str:
    """escape special characters for text blocks"""
    for char, replace in ESCAPE_CDATA.items():
        if char in text:
            text = text.replace(char, replace)
    return text

def escape_attrib(text: str) -> str:
    """escape special characters for attributes"""
    for char, replace in ESCAPE_ATTRIB.items():
        if char in text:
            text = text.replace(char, replace)
    return text

def unescape(text: str) -> str:
    """unescape special characters for attributes"""
    # process common xml escape sequences
    for char, replace in UNESCAPE_ATTRIB.items():
        if char in text:
            text = text.replace(char, replace)
    # process remaining charrefs
    for match in find_charrefs(text):
        char = match.strip('#&;')
        if len(char) % 2 == 1 and char[0] == 'x':
            rawchar = bytes.fromhex(char[1:]).decode('latin1')
        elif not char.isdigit():
            raise ValueError('invalid charref', match)
        else:
            rawchar = chr(int(char))
        text = text.replace(match, rawchar)
    return text
