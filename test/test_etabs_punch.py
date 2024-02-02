import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).parent.parent
sys.path.insert(0, str(punch_path))
from osafe_py_widgets import etabs_punch
document= FreeCAD.newDocument()
etabs = etabs_punch.EtabsPunch(beam_names=['114', '115', '116'])

# def test_create_vectors():
# 	etabs.create_vectors()
# 	assert True

def test_create_slabs_plan():
    etabs.create_slabs_plan()

def test_create_columns():
    etabs.create_columns()

def test_import_load_combos():
    etabs = etabs_punch.EtabsPunch()
    etabs.import_data(import_load_combos=True)

if __name__ == '__main__':
    test_import_load_combos()