import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).absolute().parent.parent.parent
sys.path.insert(0, str(punch_path))
import etabs_punch
document= FreeCAD.newDocument()
etabs = etabs_punch.EtabsPunch(beam_names=['114', '115', '116'])

# def test_create_vectors():
# 	etabs.create_vectors()
# 	assert True

def test_create_slabs_plan():
    etabs.create_slabs_plan()

def test_create_segments():
    etabs.create_segments()

def test_create_foundation():
    etabs.create_foundation()
    assert len(etabs.foundation.Shape.Faces) > 1
def test_create_punches():
    etabs.create_foundation()
    # etabs.create_foundation(['21', '24', '27', '30', '39', '27'])
    punches = etabs.create_punches()
    document.recompute()
    assert len(punches) == 11
    p1 = punches[0]
    assert p1.Ratio == '0.0'
    document.recompute()
    # assert p1.Ratio == '.5'
    assert type(p1.combos_load) == dict
    assert len(p1.combos_load.keys()) == 35


if __name__ == '__main__':
    test_create_segments()