import math
import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
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

def test_rotated_punch():
    foun = document_base_plate.Foundation
    col = document_base_plate.getObjectsByLabel('C1_Story1')[0]
    p = punch.make_punch(foun, col)
    p.Proxy.execute(p)
    # Test Location
    for angle in range(0, 400, 10):
        col.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),angle))
        document_base_plate.recompute()
        assert p.Location == 'Corner 1'
    # Test Ratio
    sec = col.Base
    sec.Height = 500
    sec.Width = 500
    # col.Proxy
    col.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    document_base_plate.recompute()
    assert col.Shape.BoundBox.XLength == 500
    assert col.Shape.BoundBox.YLength == 500
    # document_base_plate.recompute()
    for i in range(0, 90, 10):
        col.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),i))
        p.Proxy.execute(p)
        r1 = p.Ratio
        print(20 * '=' + '\n')
        print(i, p.Ratio)
        print(20 * '=' + '\n')
        for angle in range(i+90, 720, 90):
            col.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),angle))
            p.Proxy.execute(p)
            # document_base_plate.recompute()
            print(p.angle, p.Ratio)
            assert pytest.approx(float(r1), abs=.01) == pytest.approx(float(p.Ratio), abs=.01)
    
def test_punch_reinforcement():
    foun = document_base_plate.Foundation
    col = document_base_plate.getObjectsByLabel('C1_Story1')[0]
    p = punch.make_punch(foun, col)
    p.Use_Reinforcement = True
    p.Proxy.execute(p)
    assert True




if __name__ == '__main__':
    test_make_punch()