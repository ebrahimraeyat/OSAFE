import math
import sys
from pathlib import Path

import pytest

FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD
import Part

filename_base_foundation = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'base_foundation.FCStd'
document_base_foundation = FreeCAD.openDocument(str(filename_base_foundation))


punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import etabs_foundation


def test_make_foundation():
    bfs = []
    for o in document_base_foundation.Objects:
        if o.Proxy.Type == 'BaseFoundation':
            bfs.append(o)
    ret = etabs_foundation.make_foundation(base_foundations=bfs)
    assert True

def test_change_foundation_height():
    bfs = []
    for o in document_base_foundation.Objects:
        if hasattr(o, 'Proxy') and o.Proxy.Type == 'BaseFoundation':
            bfs.append(o)
    ret = etabs_foundation.make_foundation(base_foundations=bfs)
    ret.height = 810
    document_base_foundation.recompute([ret])
    assert ret.height_punch.Value == 810




if __name__ == '__main__':
    test_get_xy_strips()