import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD



punch_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(punch_path))
from osafe_objects import osafe_rebar

filename_rashidzadeh = Path(__file__).parent.parent / 'test_files' / 'freecad' / 'rashidzadeh.FCStd'



def test_make_rebars():
    doc = FreeCAD.openDocument(str(filename_rashidzadeh))
    rebars = osafe_rebar.make_rebars()
    FreeCAD.ActiveDocument.recompute()
    assert len(rebars.Group) == len(doc.Foundation.base_foundations)
    for rebar in rebars.Group:
        assert not rebar.Shape.isNull()

def test_make_rebar_from_scratch():
    doc = FreeCAD.newDocument()
    rebar = osafe_rebar.make_rebar_from_scratch(doc=doc)
    FreeCAD.ActiveDocument.recompute()
    assert not rebar.Shape.isNull()

if __name__ == '__main__':
    test_make_rebars()