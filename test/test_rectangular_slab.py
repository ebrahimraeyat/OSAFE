import sys
from pathlib import Path

FREECADPATH = str(Path(sys.executable).parent)
sys.path.append(FREECADPATH)

import FreeCAD


punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))

from osafe_objects.rectangular_slab import make_rectangular_slab

def test_make_rectangular_slab():
    from beam import make_beam
    FreeCAD.newDocument()
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1000, 0, 0)
    p3 = FreeCAD.Vector(3000, 2000, 0)
    b1 = make_beam(p1, p2)
    b2 = make_beam(p2, p3)
    make_rectangular_slab(
            beams=[b1, b2],
            )


if __name__ == '__main__':
    test_make_rectangular_slab()