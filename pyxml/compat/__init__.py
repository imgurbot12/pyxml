"""
XML Compatability layer to replace standard xml library
"""
import sys

#** Variables **#
__all__ = ['monkey_patch']

#** Functions **#

def monkey_patch(*modules):
    """
    monkey patch xml element-tree library to use compat modules
    """
    modules = modules or ['ElementTree', 'ElementPath']
    for module in modules:
        if module == 'ElementTree':
            from . import ElementTree
            import xml.etree.ElementTree
            xml.etree.ElementTree = ElementTree
            sys.modules['xml.etree.ElementTree'] = ElementTree
        elif module == 'ElementPath':
            from . import ElementPath
            import xml.etree.ElementPath
            xml.etree.ElementPath = ElementPath
            sys.modules['xml.etree.ElementPath'] = ElementPath
        else:
            raise ValueError('invalid module', module)
