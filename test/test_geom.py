import sys
from pathlib import Path

FREECADPATH = str(Path(sys.executable).parent)
sys.path.append(FREECADPATH)

import FreeCAD


punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))

from old_punch import geom  

def test_make_column():
    bx = 400
    by = 600
    center = FreeCAD.Vector(1000, 1000, 0)
    d = {}
    FreeCAD.newDocument()
    col = geom.make_column(bx, by, center, d)
    assert hasattr(col, 'Base') and hasattr(col.Base, 'Height')
    assert col.Base.Height == 600


if __name__ == '__main__':
    test_make_column()