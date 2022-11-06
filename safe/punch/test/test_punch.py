import math
import sys
from pathlib import Path

import pytest

FREECADPATH = 'H:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD
import Part

filename_base_plate = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'base_plate.FCStd'
document_base_plate = FreeCAD.openDocument(str(filename_base_plate))


punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import punch


def test_make_punch():
    foun = document_base_plate.Foundation
    col = document_base_plate.getObjectsByLabel('C1_Story1')[0]
    p = punch.make_punch(foun, col)
    p.Proxy.execute(p)
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