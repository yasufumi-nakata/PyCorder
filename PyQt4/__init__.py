# Minimal PyQt4 compatibility layer backed by PySide6

from . import Qt as Qt  # re-export Qt shim

# Optional submodules for legacy imports
from . import QtCore as QtCore  # noqa: F401
from . import QtGui as QtGui    # noqa: F401

# Provide uic compatibility
from . import uic as uic  # noqa: F401

# Qwt5 shim (very minimal)
from . import Qwt5 as Qwt5  # noqa: F401

__all__ = [
    "Qt",
    "QtCore",
    "QtGui",
    "uic",
    "Qwt5",
]




