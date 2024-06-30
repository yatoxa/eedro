from typing import Optional

from . import __version__


def get_version() -> Optional[str]:
    return __version__.VERSION
