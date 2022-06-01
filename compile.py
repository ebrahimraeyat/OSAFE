import os
import compileall
import shutil

from pathlib import Path

shutil.rmtree(Path("__pycache__"))
compileall.compile_file('OSAFEGui.py')
shutil.copy(Path('__pycache__') / 'OSAFEGui.cpython-38.pyc', Path('OSAFEGui.pyc'))