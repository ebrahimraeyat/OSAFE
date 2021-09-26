import sys
from pathlib import Path
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import punch_funcs  

def test_sort_vertex():
    points = [[0,0], [1,1], [1,0], [0,1]]
    points = punch_funcs.sort_vertex(points)
    assert points == [[0, 0], [0, 1], [1, 1], [1, 0]]

if __name__ == '__main__':
    pass