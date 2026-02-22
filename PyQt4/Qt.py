# -*- coding: utf-8 -*-
"""
Qt shim to let legacy PyQt4-style imports run on top of PySide6.
This provides commonly used classes and functions with minimal coverage
for this project (signals via old-style strings, QMessageBox, QFileDialog,
QApplication, QWidget, QFrame, QPen, QFont, QColor, QRect, QPoint, etc.).
"""
from PySide6 import QtCore, QtGui, QtWidgets

# Expose common namespaces under a single module like PyQt4.Qt
Qt = QtCore.Qt

# Widgets commonly referenced
QApplication = QtWidgets.QApplication
QApplication.UnicodeUTF8 = object()


def _qt4_translate(context, text, disambiguation=None, encoding=None):
    # PyQt4 used a four-argument translate that accepted an encoding flag.
    # Qt6 dropped the encoding parameter, so ignore it here for compatibility.
    if disambiguation is None:
        return QtCore.QCoreApplication.translate(context, text)
    return QtCore.QCoreApplication.translate(context, text, disambiguation)


QApplication.translate = staticmethod(_qt4_translate)
QWidget = QtWidgets.QWidget
QDialog = QtWidgets.QDialog
QMainWindow = QtWidgets.QMainWindow
QMessageBox = QtWidgets.QMessageBox
QFileDialog = QtWidgets.QFileDialog
QFrame = QtWidgets.QFrame
QProgressBar = QtWidgets.QProgressBar
QLabel = QtWidgets.QLabel
QPen = QtGui.QPen
QFont = QtGui.QFont
QColor = QtGui.QColor
QRect = QtCore.QRect
QPoint = QtCore.QPoint
QSize = QtCore.QSize
QDir = QtCore.QDir
QTableView = QtWidgets.QTableView
QHeaderView = QtWidgets.QHeaderView
QAbstractItemView = QtWidgets.QAbstractItemView
QStyledItemDelegate = QtWidgets.QStyledItemDelegate
QComboBox = QtWidgets.QComboBox
QPlainTextEdit = QtWidgets.QPlainTextEdit
QSpinBox = QtWidgets.QSpinBox
QDoubleSpinBox = QtWidgets.QDoubleSpinBox
QAbstractTableModel = QtCore.QAbstractTableModel
QModelIndex = QtCore.QModelIndex


class QMetaType:
    Bool = 1
    QString = 2


class QVariant:
    def __init__(self, value=None):
        self._value = value

    def isValid(self):
        return self._value is not None

    def type(self):
        v = self._value
        if isinstance(v, bool):
            return QMetaType.Bool
        # treat everything else as non-bool (string/number)
        return QMetaType.QString

    def toBool(self):
        return bool(self._value)

    def toInt(self):
        try:
            return int(self._value), True
        except Exception:
            return 0, False

    def toDouble(self):
        try:
            return float(self._value), True
        except Exception:
            return 0.0, False

    def toString(self):
        return str(self._value)

    def toStringList(self):
        if isinstance(self._value, (list, tuple)):
            return [str(x) for x in self._value]
        return []


class _QStringHelper(str):
    @staticmethod
    def number(n):
        return str(n)

    def toFloat(self):
        try:
            return float(self), True
        except Exception:
            return 0.0, False

    def toDouble(self):
        return self.toFloat()

    def toInt(self):
        try:
            return int(float(self)), True
        except Exception:
            return 0, False

QString = _QStringHelper  # legacy alias


def _wrap_qstring_return(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str) and not isinstance(result, _QStringHelper):
            return _QStringHelper(result)
        return result
    return wrapper


for _cls, _methods in (
    (QtWidgets.QComboBox, ('currentText', 'itemText')),
    (QtWidgets.QLineEdit, ('text', 'displayText')),
):
    for _name in _methods:
        if hasattr(_cls, _name):
            setattr(_cls, _name, _wrap_qstring_return(getattr(_cls, _name)))

# Version string expected by legacy code
try:
    QT_VERSION_STR = QtCore.qVersion()
except Exception:
    QT_VERSION_STR = "6"

# Old-style SIGNAL/SLOT compatibility
class _SignalProxy(object):
    def __init__(self, obj):
        self._obj = obj

    def __call__(self, signature):
        # Return a wrapper that emits via dynamic signal map
        # We create/lookup a QtCore.Signal dynamically on the instance
        name = signature.split('(')[0]
        # Maintain a map on the object
        if not hasattr(self._obj, "__legacy_signals__"):
            self._obj.__legacy_signals__ = {}
        signals = self._obj.__legacy_signals__
        if name not in signals:
            # Create a Python signal using QObject's meta-object is non-trivial at runtime.
            # Instead, we emulate emit/connect using a list of python callables.
            signals[name] = []
        
        class _Emitter(object):
            def __init__(self, obj, name):
                self._obj = obj
                self._name = name

            def connect(self, slot):
                self._obj.__legacy_signals__[self._name].append(slot)

            def emit(self, *args, **kwargs):
                for cb in list(self._obj.__legacy_signals__.get(self._name, [])):
                    cb(*args, **kwargs)

        return _Emitter(self._obj, name)


def SIGNAL(signature):
    try:
        return QtCore.SIGNAL(signature)
    except AttributeError:
        return signature


def SLOT(signature):
    try:
        return QtCore.SLOT(signature)
    except AttributeError:
        return signature


class QObject(QtCore.QObject):
    # Provide legacy helpers only if needed; native PySide6 connect/emit usually works
    def emit(self, signal, *args):
        # best-effort legacy emit when used with string signatures
        if not hasattr(self, 'SIGNAL'):
            self.SIGNAL = _SignalProxy(self)
        self.SIGNAL(signal).emit(*args)

    def connect(self, obj, signal, slot):  # noqa: A003 - keep legacy name
        if isinstance(signal, str):
            if not hasattr(obj, 'SIGNAL'):
                obj.SIGNAL = _SignalProxy(obj)
            obj.SIGNAL(signal).connect(slot)
            return True
        if hasattr(signal, 'connect'):
            signal.connect(slot)
            return True
        raise AttributeError("Unsupported signal type: %r" % (signal,))


# Patch PySide6 QObject with legacy helpers
QtCore.QObject.emit = QObject.emit
QtCore.QObject.connect = QObject.connect


# Inject mixin behavior into key widgets so .connect/.emit is available
# Avoid altering Qt class hierarchies to prevent instability

# Namespace shortcuts expected by code
class QStringList(list):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            super(QStringList, self).__init__([args[0]])
        else:
            super(QStringList, self).__init__(*args, **kwargs)

QDir = QtCore.QDir

# Re-export submodules for import style from PyQt4 import Qt; then Qt.Qt etc.
__all__ = [
    'Qt', 'QApplication', 'QWidget', 'QDialog', 'QMainWindow', 'QMessageBox', 'QFileDialog',
    'QFrame', 'QProgressBar', 'QLabel', 'QPen', 'QFont', 'QColor', 'QRect', 'QPoint', 'QDir',
    'QTableView', 'QHeaderView', 'QAbstractItemView', 'QStyledItemDelegate', 'QComboBox',
    'QPlainTextEdit', 'QSpinBox', 'QDoubleSpinBox', 'QAbstractTableModel', 'QModelIndex',
    'QObject', 'SIGNAL', 'SLOT', 'QT_VERSION_STR', 'QString', 'QStringList', 'QMetaType', 'QVariant'
]
