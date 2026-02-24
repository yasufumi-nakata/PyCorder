# Very small Qwt5 compatibility shim using pyqtgraph for plotting.
# Only covers what display.py/impedance.py need.

import pyqtgraph as pg
from PySide6 import QtWidgets, QtGui, QtCore

QWT_VERSION_STR = "5.99-shim"

class QwtLegend(QtWidgets.QListWidget):
    ClickableItem = 1
    def __init__(self, *args):
        super(QwtLegend, self).__init__(*args)
        self._items = []
    def setItemMode(self, mode):
        pass
    def legendItems(self):
        return self._items
    def itemCount(self):
        return len(self._items)
    def contentsWidget(self):
        return self
    def verticalScrollBar(self):
        return self
    def sizeHint(self):
        return super().sizeHint()


class QwtText:
    PaintUsingTextFont = 1
    def __init__(self, text=''):
        self._text = str(text)
        self._color = QtGui.QColor('black')
        self._font = QtGui.QFont()
    def setText(self, text):
        self._text = str(text)
    def setFont(self, f):
        self._font = f
    def setColor(self, c):
        self._color = c
    def setPaintAttribute(self, attr):
        pass
    def text(self):
        return self._text


class QwtPlot(pg.PlotWidget):
    xTop = 2
    xBottom = 0
    yLeft = 1
    LeftLegend = 0
    def __init__(self, *args, **kwargs):
        super(QwtPlot, self).__init__(*args, **kwargs)
        self._legend = QwtLegend()
        self._grid = None
    def setCanvasBackground(self, color):
        if isinstance(color, (tuple, list)) and color:
            color = color[0]
        if not isinstance(color, QtGui.QColor):
            color = QtGui.QColor(color)
        self.setBackground(color)
    def insertLegend(self, legend, where):
        self._legend = legend
    def legend(self):
        return self._legend
    def setAxisTitle(self, axis, title):
        pass
    def setAxisMaxMajor(self, axis, val):
        pass
    def setAxisMaxMinor(self, axis, val):
        pass
    def setAxisFont(self, axis, font):
        pass
    def setAxisScaleDraw(self, axis, draw):
        pass
    def enableAxis(self, axis, on):
        pass
    def setAxisScale(self, axis, vmin, vmax, step=None):
        if axis == self.xBottom:
            self.setXRange(vmin, vmax)
        else:
            self.setYRange(vmin, vmax)
    def plotLayout(self):
        return self
    def canvasMargin(self, which):
        return 0
    def replot(self):
        self.repaint()
    def axisScaleDiv(self, axis):
        class _R: 
            def range(self):
                return 10.0
        return _R()


class QwtPlotGrid:
    def __init__(self):
        pass
    def enableY(self, on):
        pass
    def enableX(self, on):
        pass
    def enableXMin(self, on):
        pass
    def setMajPen(self, pen):
        pass
    def setMinPen(self, pen):
        pass
    def attach(self, plot):
        plot._grid = self


class QwtPlotCurve(pg.PlotDataItem):
    PaintFiltered = 1
    Lines = 0
    Sticks = 1
    NoCurve = 2
    def __init__(self, title=None):
        if title is None:
            title = QwtText('')
        super(QwtPlotCurve, self).__init__(x=[], y=[])
        self._title = title
        self._style = self.Lines
        self._pen_color = QtGui.QColor('white')
    class _PenProxy:
        def __init__(self, color):
            self.color = color
    def pen(self):
        return self._PenProxy(self._pen_color)
    def setPen(self, pen):
        if hasattr(pen, 'color'):
            if callable(pen.color):
                color = pen.color()
            else:
                color = pen.color
        else:
            color = pen
        if not isinstance(color, QtGui.QColor):
            color = QtGui.QColor(color)
        self._pen_color = color
        super(QwtPlotCurve, self).setPen(pg.mkPen(color))
    def setYAxis(self, axis):
        pass
    def setPaintAttribute(self, attr):
        pass
    def attach(self, plot):
        plot.addItem(self)
    def detach(self):
        self.setVisible(False)
    def title(self):
        return self._title
    def setTitle(self, t):
        self._title = t
    def setData(self, x, y):
        super().setData(x, y)
    def setStyle(self, style):
        self._style = style
        if style == self.Sticks:
            try:
                self.setFillLevel(0)
            except Exception:
                pass
        else:
            try:
                self.setFillLevel(None)
            except Exception:
                pass


class QwtSymbol:
    VLine = 1
    def __init__(self):
        self._style = None
        self._size = 10
    def setStyle(self, s):
        self._style = s
    def setSize(self, s):
        self._size = s


class QwtPlotMarker(pg.InfiniteLine):
    NoLine = 0
    def __init__(self):
        super(QwtPlotMarker, self).__init__(angle=90)
        self.sampleCounter = 0
    def setLabel(self, txt):
        pass
    def setLabelAlignment(self, align):
        pass
    def setLineStyle(self, style):
        pass
    def setXValue(self, x):
        self.setPos(x)
    def setYValue(self, y):
        pass
    def setSymbol(self, sym):
        pass
    def attach(self, plot):
        plot.addItem(self)
    def detach(self):
        self.setVisible(False)


class QwtScaleDraw:
    RightScale = 0
    def __init__(self, *args):
        pass
    @staticmethod
    def invalidateCache(obj):
        pass


class QwtScaleDiv:
    def __init__(self, vmin, vmax, a, ticks, b):
        self._vmin = vmin
        self._vmax = vmax
        self._ticks = ticks


class QwtPlotScaleItem:
    def __init__(self, where):
        self._div = None
    def setBorderDistance(self, d):
        pass
    def attach(self, plot):
        pass
    def setScaleDiv(self, div):
        self._div = div


QwtText = QwtText
QwtPlot = QwtPlot
QwtPlotGrid = QwtPlotGrid
QwtPlotCurve = QwtPlotCurve
QwtSymbol = QwtSymbol
QwtPlotMarker = QwtPlotMarker
QwtScaleDraw = QwtScaleDraw
QwtScaleDiv = QwtScaleDiv
QwtPlotScaleItem = QwtPlotScaleItem
QwtLegend = QwtLegend
