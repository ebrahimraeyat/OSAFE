import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
from opening import make_opening
document= FreeCAD.newDocument()

def test_make_opening():
    x1 = 10
    x2 = 25
    y1 = 7
    y2 = 17
    p1=FreeCAD.Vector(x1, y1, 0)
    p2=FreeCAD.Vector(x2, y1, 0)
    p3=FreeCAD.Vector(x2, y2, 0)
    p4=FreeCAD.Vector(x1, y2, 0)
    points = [p1, p2, p3, p4]
    obj = make_opening(
            points=points,
            height = 3,
            )
    assert obj.plan.Area == 15 * 10


if __name__ == '__main__':
    test_make_opening()
