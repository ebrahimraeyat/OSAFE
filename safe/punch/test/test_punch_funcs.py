import math
import sys
from pathlib import Path

import pytest
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD
import Part

filename = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'strip.FCStd'
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
    # face0 = Part.Face(Part.makePolygon(points[0]))
    # plan = Part.Face(document.Foundation.plane_without_openings.OuterWire)
    # assert pytest.approx(face0.Area, abs=.1) == plan.Area

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
    

def test_get_points_connections_from_slabs():
    slabs = document_mat.Foundation.tape_slabs
    points_slabs = punch_funcs.get_points_connections_from_slabs(slabs)
    assert len(points_slabs) == 11

def test_extend_two_points():
    # horizontal line
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    new_p1, new_p2 = punch_funcs.extend_two_points(p1, p2, 1)
    assert new_p1 == FreeCAD.Vector(-1, 0, 0)
    assert new_p2 == FreeCAD.Vector(2, 0, 0)
    # vertical line
    p2 = FreeCAD.Vector(0, 1, 0)
    new_p1, new_p2 = punch_funcs.extend_two_points(p1, p2, 1)
    assert new_p1 == FreeCAD.Vector(0, -1, 0)
    assert new_p2 == FreeCAD.Vector(0, 2, 0)
    # inverse p1 and p2
    p2 = FreeCAD.Vector(0, 0, 0)
    p1 = FreeCAD.Vector(1, 0, 0)
    new_p1, new_p2 = punch_funcs.extend_two_points(p1, p2, 1)
    assert new_p2 == FreeCAD.Vector(-1, 0, 0)
    assert new_p1 == FreeCAD.Vector(2, 0, 0)
    
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 1, 0)
    new_p1, new_p2 = punch_funcs.extend_two_points(p1, p2, math.sqrt(2))
    assert new_p1 == FreeCAD.Vector(-1, -1, 0)
    assert new_p2 == FreeCAD.Vector(2, 2, 0)

def test_get_width_points():
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    w = .5
    points = punch_funcs.get_width_points(p1, p2, w)
    assert len(points) == 4
    assert FreeCAD.Vector(0, -.5, 0) in points
    assert FreeCAD.Vector(0, .5, 0) in points
    assert FreeCAD.Vector(1, -.5, 0) in points
    assert FreeCAD.Vector(1, .5, 0) in points

def test_get_offset_points():
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    offset = .5
    points = punch_funcs.get_offset_points(p1, p2, offset)
    assert len(points) == 2
    assert FreeCAD.Vector(0, .5, 0) in points
    assert FreeCAD.Vector(1, .5, 0) in points

def test_get_common_part_of_slabs():
    s0 = document.Slab
    s3 = document.Slab003
    s5 = document.Slab005
    comm = punch_funcs.get_common_part_of_slabs((s0, s3, s5))
    assert len(comm.Faces) == 1
    assert len(comm.Edges) == 6

def test_get_common_parts_of_foundation_slabs():
    points_commons = punch_funcs.get_common_parts_of_foundation_slabs(document.Foundation)
    assert len(points_commons) == 11

def test_get_foundation_plane_without_openings():
    plan = punch_funcs.get_foundation_plane_without_openings(document.Foundation)
    assert len(plan.Faces) == 1
    assert len(plan.Edges) == 30

def test_get_foundation_plan_with_openings():
    plan_with_openings, plan_without_openings = punch_funcs.get_foundation_plan_with_openings(document.Foundation)
    assert len(plan_with_openings.Faces) == 1
    assert len(plan_with_openings.Edges) == 34
    assert len(plan_without_openings.Faces) == 1
    assert len(plan_without_openings.Edges) == 30

def test_get_foundation_plan_with_holes():
    plan_with_openings, plan_without_openings, holes = punch_funcs.get_foundation_plan_with_holes(document.Foundation)
    assert len(plan_with_openings.Faces) == 1
    assert len(plan_with_openings.Edges) == 34
    assert len(plan_without_openings.Faces) == 1
    assert len(plan_without_openings.Edges) == 30
    assert len(holes) == 6
    for hole in holes:
        assert isinstance(hole, Part.Face)
    plan_with_openings, plan_without_openings, holes = punch_funcs.get_foundation_plan_with_holes(document_mat.Foundation)
    assert len(plan_with_openings.Faces) == 1
    assert len(plan_with_openings.Edges) == 11
    assert len(plan_without_openings.Faces) == 1
    assert len(plan_without_openings.Edges) == 7
    assert len(holes) == 1
    for hole in holes:
        assert isinstance(hole, Part.Face)

def test_get_points_of_foundation_plan_and_holes():
    points = punch_funcs.get_points_of_foundation_plan_and_holes(document.Foundation)
    assert len(points) == 7
    assert len(points[0]) == 7

def test_punch_area_edges():
    obj = document.Punch002
    d = obj.foundation.d.Value
    x = obj.bx + d
    y = obj.by + d
    offset_shape = punch_funcs.rectangle_face(obj.center_of_load, x, y)
    foun_plan = obj.foundation.plane.copy()
    edges = punch_funcs.punch_area_edges(foun_plan, offset_shape)
    assert len(edges) == 3

def test_punch_null_edges():
    obj = document.Punch002
    d = obj.foundation.d.Value
    x = obj.bx + d
    y = obj.by + d
    offset_shape = punch_funcs.rectangle_face(obj.center_of_load, x, y)
    foun_plan = obj.foundation.plane.copy()
    edges = punch_funcs.punch_area_edges(foun_plan, offset_shape)
    null_edges, common_edges = punch_funcs.punch_null_edges(foun_plan, offset_shape, edges)
    assert null_edges == [0, 1, 1, 0, 0, 1]
    assert len(null_edges) == 6
    assert len(common_edges) == 6




if __name__ == '__main__':
    test_punch_null_edges()