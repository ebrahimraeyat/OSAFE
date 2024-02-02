import math
import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD

filename_base_plate = Path(__file__).parent / 'test_files' / 'freecad' / 'base_plate.FCStd'
document_base_plate = FreeCAD.openDocument(str(filename_base_plate))


punch_path = Path(__file__).parent.parent
sys.path.insert(0, str(punch_path))

from osafe_objects import beam, punch

def test_make_beam():
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    beam.make_beam(p1, p2)
    assert True

def test_punch_reinforcement():
    foun = document_base_plate.Foundation
    col = document_base_plate.getObjectsByLabel('C1_Story1')[0]
    p = punch.make_punch(foun, col)
    p.Use_Reinforcement = True
    p.Proxy.execute(p)
    assert True




if __name__ == '__main__':
    test_make_punch()