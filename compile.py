import os
import compileall
import shutil

from pathlib import Path

shutil.rmtree(Path("__pycache__"))
compileall.compile_file('civilGui.py')
shutil.copy(Path('__pycache__') / 'civilGui.cpython-38.pyc', Path('civilGui.pyc'))