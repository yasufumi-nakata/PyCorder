# -*- coding: utf-8 -*-
'''
Load required libraries and check versions  

PyCorder ActiChamp Recorder

------------------------------------------------------------

Copyright (C) 2010, Brain Products GmbH, Gilching

PyCorder is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCorder. If not, see <http://www.gnu.org/licenses/>.

------------------------------------------------------------


@author: Norbert Hauser
@date: $Date: 2011-03-24 16:03:45 +0100 (Do, 24 Mrz 2011) $
@version: 1.0

B{Revision:} $LastChangedRevision: 62 $
'''


'''
------------------------------------------------------------
CHECK LIBRARY DEPENDENCIES
------------------------------------------------------------
'''

import re
import sys

import_log = ""

missing_dependencies = []
version_mismatches = []

MIN_PYTHON = (3, 9, 0)
MINIMUM_VERSIONS = {
    "NumPy": "1.20.0",
    "SciPy": "1.8.0",
    "PyQt": "6.2.0",
    "PyQwt": "0.12.0",
    "lxml": "4.6.0",
}


def _append(msg):
    global import_log
    import_log += msg
    return msg


def _record_missing(name, msg):
    if name not in missing_dependencies:
        missing_dependencies.append(name)
    _append(msg)


def _record_mismatch(name, msg):
    if name not in version_mismatches:
        version_mismatches.append(name)
    _append(msg)


def _to_version_tuple(version_string):
    """Convert a loose version string into a comparable integer tuple."""
    parts = []
    for item in re.split(r"[^\d]+", str(version_string)):
        if not item:
            continue
        parts.append(int(item))
        if len(parts) >= 3:
            break
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def _is_at_least(current, minimum):
    return _to_version_tuple(current) >= _to_version_tuple(minimum)


def _check_minimum(name, current, minimum):
    if not _is_at_least(current, minimum):
        _record_mismatch(
            name,
            "- %s is too old (%s), please install %s >= %s\r\n" % (name, current, name, minimum),
        )


# try to import python libraries, check versions
if sys.version_info < MIN_PYTHON:
    _record_mismatch(
        "Python",
        "- Python %i.%i+ is required (current: %s)\r\n"
        % (MIN_PYTHON[0], MIN_PYTHON[1], sys.version.split()[0]),
    )

try:
    import numpy as np
    _check_minimum("NumPy", np.__version__, MINIMUM_VERSIONS["NumPy"])
except ImportError:
    _record_missing(
        "NumPy",
        "- NumPy missing, please install NumPy >= %s\r\n" % (MINIMUM_VERSIONS["NumPy"],),
    )

try:
    import scipy as sc
    _check_minimum("SciPy", sc.__version__, MINIMUM_VERSIONS["SciPy"])
except ImportError:
    _record_missing(
        "SciPy",
        "- SciPy missing, please install SciPy >= %s\r\n" % (MINIMUM_VERSIONS["SciPy"],),
    )

try:
    from PyQt4 import Qt
    qt_version = getattr(Qt, "QT_VERSION_STR", "0.0.0")
    _check_minimum("PyQt", qt_version, MINIMUM_VERSIONS["PyQt"])
except ImportError:
    _record_missing(
        "PyQt",
        "- PyQt missing, please install PySide6 and local PyQt4 compatibility shim\r\n",
    )

try:
    from PyQt4 import Qwt5 as Qwt
    qwt_version = getattr(Qwt, "QWT_VERSION_STR", "0.0.0")
    _check_minimum("PyQwt", qwt_version, MINIMUM_VERSIONS["PyQwt"])
except ImportError:
    _record_missing(
        "PyQwt",
        "- PyQwt missing, please install pyqtgraph (Qwt compatibility layer)\r\n",
    )

try:
    from lxml import etree
    _check_minimum("lxml", etree.__version__, MINIMUM_VERSIONS["lxml"])
except ImportError:
    _record_missing(
        "lxml",
        "- lxml missing, please install lxml >= %s\r\n" % (MINIMUM_VERSIONS["lxml"],),
    )
    


def dependency_status():
    """Return collected dependency info for diagnostics."""
    return {
        'missing': list(missing_dependencies),
        'version_mismatch': list(version_mismatches),
        'log': import_log.strip(),
    }


def has_all_dependencies():
    return len(missing_dependencies) == 0

