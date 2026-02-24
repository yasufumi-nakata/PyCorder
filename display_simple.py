# -*- coding: utf-8 -*-
"""Stable pyqtgraph-based scope view used on platforms where Qwt shim is unstable."""

from __future__ import annotations

from PyQt4 import Qt
import numpy as np
import pyqtgraph as pg
import threading

from modbase import *


class DISP_ScopeSimple(ModuleBase):
    """Lightweight signal display.

    This module focuses on stability: it plots a few channels from incoming
    data and avoids the legacy Qwt API surface.
    """

    def __init__(self, *args, **keys):
        ModuleBase.__init__(self, usethread=True, name="Display", **keys)

        self._pane = Qt.QFrame()
        self._pane.setObjectName("DisplaySimple")
        self._pane.setMinimumSize(Qt.QSize(400, 200))
        layout = Qt.QVBoxLayout(self._pane)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setLabel("bottom", "Samples")
        self.plot.setLabel("left", "Amplitude (uV)")
        layout.addWidget(self.plot)

        self._lock = threading.Lock()
        self._sample_rate = 500.0
        self._max_channels = 8
        self._history_samples = 4000
        self._pending = None
        self._buffer = None
        self._curves = []
        self._curve_colors = ["#005f73", "#0a9396", "#ee9b00", "#ca6702",
                              "#bb3e03", "#ae2012", "#9b2226", "#3a86ff"]
        self._update_requested = False
        self.startTimer(50)

    def get_display_pane(self):
        return self._pane

    def process_update(self, params):
        if params is not None:
            self._sample_rate = float(getattr(params, "sample_rate", 500.0))
            channel_count = min(len(params.channel_properties), self._max_channels)
            with self._lock:
                if channel_count <= 0:
                    self._buffer = np.zeros((0, self._history_samples), dtype=float)
                else:
                    self._buffer = np.zeros((channel_count, self._history_samples), dtype=float)
                self._pending = None
                self._update_requested = True
            self._ensure_curves(channel_count)
        return params

    def process_start(self):
        with self._lock:
            if self._buffer is not None:
                self._buffer[:] = 0.0
            self._pending = None
            self._update_requested = True

    def process_input(self, datablock):
        if datablock is None:
            return
        if datablock.recording_mode == RecordingMode.IMPEDANCE:
            return

        data = np.asarray(datablock.eeg_channels, dtype=float)
        if data.ndim != 2 or data.shape[1] == 0:
            return
        channels = min(data.shape[0], self._max_channels)
        if channels <= 0:
            return

        with self._lock:
            if self._buffer is None or self._buffer.shape[0] != channels:
                self._buffer = np.zeros((channels, self._history_samples), dtype=float)
                self._ensure_curves(channels)
            self._pending = data[:channels].copy()
            self._update_requested = True

    def process_output(self):
        return None

    def timerEvent(self, _event):
        if not self._update_requested:
            return
        with self._lock:
            pending = self._pending
            self._pending = None
            buffer = self._buffer
            self._update_requested = False
        if buffer is None or buffer.size == 0:
            return
        if pending is not None and pending.size > 0:
            n = pending.shape[1]
            if n >= buffer.shape[1]:
                buffer[:] = pending[:, -buffer.shape[1]:]
            else:
                buffer[:, :-n] = buffer[:, n:]
                buffer[:, -n:] = pending
        self._redraw(buffer)

    def _ensure_curves(self, channel_count):
        while len(self._curves) < channel_count:
            idx = len(self._curves)
            color = self._curve_colors[idx % len(self._curve_colors)]
            curve = self.plot.plot(pen=pg.mkPen(color, width=1))
            self._curves.append(curve)
        while len(self._curves) > channel_count:
            curve = self._curves.pop()
            self.plot.removeItem(curve)

    def _redraw(self, buffer):
        x = np.arange(buffer.shape[1], dtype=float)
        spacing = 200.0
        for idx, curve in enumerate(self._curves):
            y = buffer[idx] + (len(self._curves) - idx - 1) * spacing
            curve.setData(x, y)
