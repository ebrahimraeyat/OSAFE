import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import etabs_punch
document= FreeCAD.newDocument()
etabs = etabs_punch.EtabsPunch()

def test_create_vectors():
	etabs.create_vectors()
	assert True

def test_create_slabs():
	etabs.create_slabs(['114', '115', '116'])

if __name__ == '__main__':
	test_create_slabs()