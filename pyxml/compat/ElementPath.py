"""
Compatability Layer to replace `xml.etree.ElementPath`
"""
from ..xpath import iterfind, find, findall, findtext

#** Variables **#
__all__ = [
    'iterfind',
    'find',
    'findall',
    'findtext',
]
