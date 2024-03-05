import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD



punch_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(punch_path))
from osafe_objects.osafe_rebar import make_rebars

filename_rashidzadeh = Path(__file__).parent.parent / 'test_files' / 'freecad' / 'rashidzadeh.FCStd'



def test_make_rebars():
    FreeCAD.openDocument(str(filename_rashidzadeh))
    make_rebars()
    FreeCAD.ActiveDocument.recompute()
    assert True

if __name__ == '__main__':
    test_make_rebars()