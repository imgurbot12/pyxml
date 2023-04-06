try:
    from typing import NamedTuple
    from typing import Optional
    from typing import Iterator  # incompatible
    from typing import List
    from typing import Generator  # incompatible
    from typing import Dict
    from typing import Any  # incompatible
    from typing import BinaryIO  # incompatible
    from typing import Tuple
    from typing import Callable  # incompatible?, undocumented
    from typing import Union

    from functools import wraps  # missing
    from enum import IntEnum  # missing
    import string

    from typing_extensions import Self

except:
    raise NotImplementedError

# TODO (non-exhaustive):
#  Iterator may be replace with List
#  Generator has only 1 usage at BaseLexer.iter()
#  Any has only 1 usage in Element.get()
#  Callable is undocumented, do test
#  replicate class: string, bytes, BinaryIO
