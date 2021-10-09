import sys
from pathlib import Path

import pytest
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD
import Part

filename = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / '2.FCStd'
filename_mat = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'mat.FCStd'
document= FreeCAD.openDocument(str(filename))
document_mat= FreeCAD.openDocument(str(filename_mat))


punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import punch_funcs  

def test_sort_vertex():
    points = [[0,0], [1,1], [1,0], [0,1]]
    points = punch_funcs.sort_vertex(points)
    assert points == [[0, 0], [0, 1], [1, 1], [1, 0]]

def test_get_obj_points_with_scales():
    points = punch_funcs.get_obj_points_with_scales(document.Foundation.plane_without_openings)
    assert len(points) == 3
    assert len(points[0]) == 21
    assert len(points[1]) == 21
    assert len(points[2]) == 21
    face = Part.Face(Part.makePolygon(points[0]))
    assert pytest.approx(face.Area, abs=.1) == document.Foundation.plane_without_openings.Area

def test_get_scale_area_points_with_scale():
    points = punch_funcs.get_scale_area_points_with_scale(document.Foundation.plane_without_openings)
    assert len(points) == 5
    assert len(points[-1]) == 21
    assert len(points[0]) == 22
    assert len(points[1]) == 22

def test_split_face_with_scales():
    plan = document_mat.Foundation.plane_without_openings
    faces = punch_funcs.split_face_with_scales(plan)
    assert len(faces) == 5
    area = 0
    for f in faces:
        area += f.Area
    assert pytest.approx(area, abs=.1) == plan.Area

def test_get_sub_areas_points_from_face_with_scales():
    plan = document_mat.Foundation.plane_without_openings
    points = punch_funcs.get_sub_areas_points_from_face_with_scales(plan)
    assert len(points) == 5
    assert len(points[-1]) == 21
    for ps in points:
        assert len(ps) == 22

def test_get_points_connections_from_slabs():
    slabs = document_mat.Foundation.tape_slabs
    points_slabs = punch_funcs.get_points_connections_from_slabs(slabs)
    assert len(points_slabs) == 11


if __name__ == '__main__':
    pass