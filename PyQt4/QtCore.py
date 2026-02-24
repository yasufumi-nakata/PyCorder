from PySide6.QtCore import *  # noqa: F401,F403


class QVariant(object):  # minimal shim for Qt4 API
    def __init__(self, value=None):
        self._value = value

    def isValid(self):
        return self._value is not None

    def type(self):
        value = self._value
        if isinstance(value, bool):
            return 1
        return 2

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


class QString(str):
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


class QStringList(list):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            super(QStringList, self).__init__([args[0]])
        else:
            super(QStringList, self).__init__(*args, **kwargs)

