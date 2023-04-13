try:
    from typing import NamedTuple
    from typing import Optional
    from typing import Iterator  # incompatible
    from typing import List
    from typing import Generator  # incompatible
    from typing import Dict
    from typing import Any  # incompatible
    from typing import BinaryIO  # implement
    from typing import Tuple
    from typing import Callable  # incompatible?, undocumented
    from typing import Union

    from functools import wraps  # missing
    from enum import IntEnum  # implement
    import string  # implement

    from typing_extensions import Self

    bytearray = list  # implement: endswith()
    bytes = list  # implement: encode(), replace(), startswith(), isdigit()

except:
    raise NotImplementedError


# TODO (non-exhaustive):
#  Remove bytes literal
#  Iterator may be replace with List
#  Generator has only 1 usage at BaseLexer.iter()
#  Any has only 1 usage in Element.get()
#  Callable is undocumented, do test
#  implement class: string, bytes, BinaryIO, bytearray

