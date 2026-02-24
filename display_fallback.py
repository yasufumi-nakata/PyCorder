# -*- coding: utf-8 -*-
"""Fallback display module used when the full scope widget cannot initialize."""

from PyQt4 import Qt
from PyQt4 import QtGui

from modbase import ModuleBase


class DISP_ScopeLite(ModuleBase):
    """Minimal placeholder display pane.

    Keeps the GUI usable when the Qwt/pyqtgraph-based scope cannot be created
    in the current Qt binding/runtime.
    """

    def __init__(self, *args, **keys):
        reason = keys.pop("reason", "")
        ModuleBase.__init__(self, usethread=False, name="Display", **keys)

        self._pane = Qt.QFrame()
        self._pane.setObjectName("DisplayFallback")
        self._pane.setFrameShape(Qt.QFrame.StyledPanel)
        layout = QtGui.QVBoxLayout(self._pane)
        layout.setContentsMargins(12, 12, 12, 12)

        title = Qt.QLabel("Scope view is unavailable in this environment.")
        title.setWordWrap(True)
        layout.addWidget(title)

        if reason:
            detail = Qt.QLabel("Reason: %s" % (reason,))
            detail.setWordWrap(True)
            layout.addWidget(detail)

        hint = Qt.QLabel("Acquisition and recording can continue using the other modules.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

    def get_display_pane(self):
        return self._pane

    def process_input(self, datablock):
        return

    def process_output(self):
        return None
