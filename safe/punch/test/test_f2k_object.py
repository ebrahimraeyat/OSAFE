import sys
from pathlib import Path


FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD

# filename_base_plate = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'base_plate.FCStd'
# document_base_plate = FreeCAD.openDocument(str(filename_base_plate))


punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))


def test_make_safe_f2k():
    FreeCAD.newDocument()
    import f2k_object
    f2k_object.make_safe_f2k()
    assert True


if __name__ == '__main__':
    test_make_safe_f2k()