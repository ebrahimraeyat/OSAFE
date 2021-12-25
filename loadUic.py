from pathlib import Path

from PySide2.QtUiTools import loadUiType

civiltools_path = Path(r"C:\Users\ebi\AppData\Roaming\FreeCAD\Mod\Civil\civilTools")
print(Path(civiltools_path / 'widgets' / 'results.ui').exists())
print(str(civiltools_path / 'widgets' / 'results.ui'))
result_window, result_base = loadUiType(str(civiltools_path / 'widgets' / 'results.ui'))
