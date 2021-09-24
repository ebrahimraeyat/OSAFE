import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
from trapezoidal_slab import make_trapezoidal_slab
document= FreeCAD.newDocument()

# def test_create_vectors():
# 	etabs.create_vectors()
# 	assert True

def test_make_trapezoidal_slab():
	obj = make_trapezoidal_slab(p1=FreeCAD.Vector(0, 16400, 0),
			   p2=FreeCAD.Vector(12210, 16400, 0),
			   layer='A',
			   design_type='column',
			   swl='25 cm',
			   swr=250,
			   ewl=250,
			   ewr=250,
			   )
	assert obj.plane.Area == 12210 * 500
	assert obj.layer == 'A'


if __name__ == '__main__':
	test_make_trapezoidal_slab()
