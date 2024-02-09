import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD



punch_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(punch_path))
from osafe_objects import base_plate


def test_make_base_plate():
    doc = FreeCAD.newDocument()
    FreeCAD.setActiveDocument(doc.Name)
    import Arch
    col = Arch.makeStructure()
    col.recompute(True)
    bx = 500
    by = 600
    bp = base_plate.make_base_plate(bx=bx, by=by, column=col.Label)
    bp.recompute(True)
    assert hasattr(col, 'base_plate')
    assert col.base_plate.Name == bp.Name
    assert bp.Bx == bx
    assert bp.By == by

if __name__ == '__main__':
    test_make_base_plate()