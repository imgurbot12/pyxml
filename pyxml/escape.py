"""
Escape/Unescape Utilities for XML Handling
"""

#** Variables **#
__all__ = ['escape_cdata', 'escape_attrib', 'unescape']

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
    '\r': '&#13;',
    '\n': '&#10;',
    '\t': '&#09;',
}

#: reverse dictionary used to unescape special characters
UNESCAPE_ATTRIB = {v:k for k,v in ESCAPE_ATTRIB.items()}

#** Functions **#

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
    for char, replace in UNESCAPE_ATTRIB.items():
        if char in text:
            text = text.replace(char, replace)
    return text

