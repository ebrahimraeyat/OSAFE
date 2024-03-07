import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD
import Part
import Draft



punch_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(punch_path))
from osafe_objects.strip import make_strip

filename_rashidzadeh = Path(__file__).parent.parent / 'test_files' / 'freecad' / 'rashidzadeh.FCStd'



def test_make_strip():
    FreeCAD.newDocument()
    # Part wire
    p11 = FreeCAD.Vector(0, 0, 0)
    p22 = FreeCAD.Vector(10000, 0, 0)
    wire = Part.Wire(Part.makeLine(p11, p22))
    strip = make_strip(base=wire)
    FreeCAD.ActiveDocument.recompute()
    assert strip.Shape.Area == 10000 * 1000
    assert strip.Shape.BoundBox.YMax == 500
    assert strip.Shape.BoundBox.YMin == -500
    # Draft wire
    wire = Draft.make_wire(wire)
    strip = make_strip(base=wire)
    FreeCAD.ActiveDocument.recompute()
    assert strip.Shape.Area == 10000 * 1000
    assert strip.Shape.BoundBox.YMax == 500
    assert strip.Shape.BoundBox.YMin == -500

if __name__ == '__main__':
    test_make_strip()