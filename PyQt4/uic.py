from PySide6 import QtUiTools

def compileUi(ui_filename, fp):
    loader = QtUiTools.QUiLoader()
    # We cannot compile to python; emulate by writing a minimal stub or raising.
    # For this project, .py files already exist in res/. If needed, we fallback.
    raise NotImplementedError("uic.compileUi is not supported in this shim. Use generated .py files.")




