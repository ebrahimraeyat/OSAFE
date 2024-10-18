import math
import sys
from pathlib import Path

import pytest
import numpy as np

FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD
import Part

filename = Path(__file__).parent / 'test_files' / 'freecad' / 'strip.FCStd'
filename_strip_foundation = Path(__file__).parent / 'test_files' / 'freecad' / 'strip_foundation.FCStd'
filename_mat = Path(__file__).parent / 'test_files' / 'freecad' / 'mat.FCStd'
filename_base_foundation = Path(__file__).parent / 'test_files' / 'freecad' / 'base_foundation.FCStd'
filename_khalaji = Path(__file__).parent / 'test_files' / 'freecad' / 'khalaji.FCStd'
filename_test = Path(__file__).parent / 'test_files' / 'freecad' / 'test.FCStd'
filename_base_plate = Path(__file__).parent / 'test_files' / 'freecad' / 'base_plate.FCStd'
filename_rashidzadeh = Path(__file__).parent / 'test_files' / 'freecad' / 'rashidzadeh.FCStd'
document= FreeCAD.openDocument(str(filename))
document_mat= FreeCAD.openDocument(str(filename_mat))
document_base_foundation = FreeCAD.openDocument(str(filename_base_foundation))
document_strip_foundation = FreeCAD.openDocument(str(filename_strip_foundation))
document_khalaji = FreeCAD.openDocument(str(filename_khalaji))
document_test = FreeCAD.openDocument(str(filename_test))
document_base_plate = FreeCAD.openDocument(str(filename_base_plate))
document_rashidzadeh = FreeCAD.openDocument(str(filename_rashidzadeh))


punch_path = Path(__file__).parent.parent
sys.path.insert(0, str(punch_path))
from osafe_funcs import osafe_funcs

def test_sort_vertex():
    points = [[0,0], [1,1], [1,0], [0,1]]
    points = osafe_funcs.sort_vertex(points)
    assert points == [[0, 0], [0, 1], [1, 1], [1, 0]]

def test_get_points_from_indirection_edges():
    v1 = FreeCAD.Vector(0, 0, 0)
    v2 = FreeCAD.Vector(2, 1, 0)
    v3 = FreeCAD.Vector(3, 3, 0)
    v4 = FreeCAD.Vector(4, 5, 0)
    v5 = FreeCAD.Vector(6, 6, 0)
    vs = (v1, v2, v3, v4, v5)
    edges = []
    for p1, p2 in zip(vs[:-1], vs[1:]):
        l = Part.makeLine(p1, p2)
        edges.append(Part.Edge(l))
    points = osafe_funcs.get_points_from_indirection_edges(edges)
    assert len(points) == 4
    assert points == [v1, v2, v4, v5]
    # one edge
    points = osafe_funcs.get_points_from_indirection_edges([edges[0]])
    assert len(points) == 2
    assert points == [v1, v2]
    #  straight line
    vs = (v1, v3, v5)
    edges = []
    for p1, p2 in zip(vs[:-1], vs[1:]):
        l = Part.makeLine(p1, p2)
        edges.append(Part.Edge(l))
    points = osafe_funcs.get_points_from_indirection_edges(edges)
    assert len(points) == 2
    assert points == [v1, v5]

def test_remove_colinear_edges():
    v1 = FreeCAD.Vector(0, 0, 0)
    v2 = FreeCAD.Vector(2, 1, 0)
    v3 = FreeCAD.Vector(3, 3, 0)
    v4 = FreeCAD.Vector(4, 5, 0)
    v5 = FreeCAD.Vector(6, 6, 0)
    vs = (v1, v2, v3, v4, v5)
    edges = []
    for p1, p2 in zip(vs[:-1], vs[1:]):
        l = Part.makeLine(p1, p2)
        edges.append(Part.Edge(l))
    es = osafe_funcs.remove_colinear_edges(edges)
    assert len(es) == 3
    # one edge
    es = osafe_funcs.remove_colinear_edges([edges[0]])
    assert len(es) == 1
    #  straight line
    vs = (v1, v3, v5)
    edges = []
    for p1, p2 in zip(vs[:-1], vs[1:]):
        l = Part.makeLine(p1, p2)
        edges.append(Part.Edge(l))
    es = osafe_funcs.remove_colinear_edges(edges)
    assert len(es) == 1
    # Face
    vs = (v1, v2, v3, v4, v1)
    wire = Part.makePolygon(vs)
    face = Part.Face(wire)
    es = osafe_funcs.remove_colinear_edges(face)
    assert isinstance(es, Part.Face)
    assert len(es.Edges) == 3

def test_get_sort_points():
    v1 = FreeCAD.Vector(0, 0, 0)
    v2 = FreeCAD.Vector(5, 0, 0)
    v3 = FreeCAD.Vector(5, 0, 0)
    v4 = FreeCAD.Vector(10, 0, 0)
    l = Part.makeLine(v1, v2)
    e1 = Part.Edge(l)
    l = Part.makeLine(v4, v3)
    e2 = Part.Edge(l)
    edges = [e1, e2]
    points = osafe_funcs.get_sort_points(edges, get_last=True)
    v11, v22, v33 = points
    assert any([
        all([
            v11.isEqual(v1, True),
            v22.isEqual(v2, True),
            v33.isEqual(v4, True),
            ]),
        all([
            v11.isEqual(v4, True),
            v22.isEqual(v2, True),
            v33.isEqual(v1, True),
            ])
    ])
    # first edge reverse
    l = Part.makeLine(v2, v1)
    e1 = Part.Edge(l)
    l = Part.makeLine(v3, v4)
    e2 = Part.Edge(l)
    edges = [e1, e2]
    points = osafe_funcs.get_sort_points(edges, get_last=True)
    v11, v22, v33 = points
    assert any([
        all([
            v11.isEqual(v1, True),
            v22.isEqual(v2, True),
            v33.isEqual(v4, True),
            ]),
        all([
            v11.isEqual(v4, True),
            v22.isEqual(v2, True),
            v33.isEqual(v1, True),
            ])
    ])

def test_split_face_with_scales():
    plan = document_mat.Foundation.plan_without_openings
    faces = osafe_funcs.split_face_with_scales(plan)
    assert len(faces) == 5
    area = 0
    for f in faces:
        area += f.Area
    assert pytest.approx(area, abs=.1) == plan.Area

def test_get_sub_areas_points_from_face_with_scales():
    plan = document_mat.Foundation.plan_without_openings
    points = osafe_funcs.get_sub_areas_points_from_face_with_scales(plan)
    assert len(points) == 5

def test_get_extended_wire_first_last_edge():
    # one edge wire
    # horizontal line one edge
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(10, 0, 0)
    e = Part.makeLine(p1, p2)
    wire = Part.Wire([e])
    e1, e2 = osafe_funcs.get_extended_wire_first_last_edge(wire, 1)
    assert e1.Length == 1
    assert e2.Length == 1
    assert e1.BoundBox.XMin == -1
    assert e1.BoundBox.XMax == 0
    assert e2.BoundBox.XMin == 10
    assert e2.BoundBox.XMax == 11
    # Negative value
    e1, e2 = osafe_funcs.get_extended_wire_first_last_edge(wire, -1)
    assert e1.Length == 8
    assert e2.Length == 8
    assert e1.BoundBox.XMin == 1
    assert e1.BoundBox.XMax == 9
    assert e2.BoundBox.XMin == 1
    assert e2.BoundBox.XMax == 9
    # two edge wire
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(5, 0, 0)
    p3 = FreeCAD.Vector(10, 0, 0)
    e1 = Part.makeLine(p1, p2)
    e2 = Part.makeLine(p2, p3)
    wire = Part.Wire([e1, e2])
    e11, e22 = osafe_funcs.get_extended_wire_first_last_edge(wire, 1)
    assert e11.Length == 1
    assert e22.Length == 1
    assert e11.BoundBox.XMin == -1
    assert e11.BoundBox.XMax == 0
    assert e22.BoundBox.XMin == 10
    assert e22.BoundBox.XMax == 11
    # Negative Value
    e11, e22 = osafe_funcs.get_extended_wire_first_last_edge(wire, -1)
    assert e11.Length == 4
    assert e22.Length == 4
    assert e11.BoundBox.XMin == 1
    assert e11.BoundBox.XMax == 5
    assert e22.BoundBox.XMin == 5
    assert e22.BoundBox.XMax == 9

def test_get_extended_wire():
    # one edge wire
    # horizontal line one edge
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(10, 0, 0)
    e = Part.makeLine(p1, p2)
    wire = Part.Wire([e])
    w, e1, e2 = osafe_funcs.get_extended_wire(wire, 1)
    assert len(w.Edges) == 3
    assert e1.Length == 1
    assert e2.Length == 1
    assert e1.BoundBox.XMin == -1
    assert e1.BoundBox.XMax == 0
    assert e2.BoundBox.XMin == 10
    assert e2.BoundBox.XMax == 11
    # Negative value
    w, e1, e2 = osafe_funcs.get_extended_wire(wire, -1)
    assert len(w.Edges) == 1
    assert e1.Length == 8
    assert e2.Length == 8
    assert e1.BoundBox.XMin == 1
    assert e1.BoundBox.XMax == 9
    assert e2.BoundBox.XMin == 1
    assert e2.BoundBox.XMax == 9
    # two edge wire
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(5, 0, 0)
    p3 = FreeCAD.Vector(10, 0, 0)
    e1 = Part.makeLine(p1, p2)
    e2 = Part.makeLine(p2, p3)
    wire = Part.Wire([e1, e2])
    w, e11, e22 = osafe_funcs.get_extended_wire(wire, 1)
    assert len(w.Edges) == 4
    assert e11.Length == 1
    assert e22.Length == 1
    assert e11.BoundBox.XMin == -1
    assert e11.BoundBox.XMax == 0
    assert e22.BoundBox.XMin == 10
    assert e22.BoundBox.XMax == 11
    # Negative Value
    w, e11, e22 = osafe_funcs.get_extended_wire(wire, -1)
    assert len(w.Edges) == 2
    assert e11.Length == 4
    assert e22.Length == 4
    assert e11.BoundBox.XMin == 1
    assert e11.BoundBox.XMax == 5
    assert e22.BoundBox.XMin == 5
    assert e22.BoundBox.XMax == 9

def test_extend_two_points():
    # horizontal line
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    new_p1, new_p2 = osafe_funcs.extend_two_points(p1, p2, 1)
    assert new_p1 == FreeCAD.Vector(-1, 0, 0)
    assert new_p2 == FreeCAD.Vector(2, 0, 0)
    # vertical line
    p2 = FreeCAD.Vector(0, 1, 0)
    new_p1, new_p2 = osafe_funcs.extend_two_points(p1, p2, 1)
    assert new_p1 == FreeCAD.Vector(0, -1, 0)
    assert new_p2 == FreeCAD.Vector(0, 2, 0)
    # inverse p1 and p2
    p2 = FreeCAD.Vector(0, 0, 0)
    p1 = FreeCAD.Vector(1, 0, 0)
    new_p1, new_p2 = osafe_funcs.extend_two_points(p1, p2, 1)
    assert new_p2 == FreeCAD.Vector(-1, 0, 0)
    assert new_p1 == FreeCAD.Vector(2, 0, 0)
    
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 1, 0)
    new_p1, new_p2 = osafe_funcs.extend_two_points(p1, p2, math.sqrt(2))
    assert new_p1 == FreeCAD.Vector(-1, -1, 0)
    assert new_p2 == FreeCAD.Vector(2, 2, 0)
    # negative value
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(10, 0, 0)
    new_p1, new_p2 = osafe_funcs.extend_two_points(p1, p2, -1)
    assert new_p1 == FreeCAD.Vector(1, 0, 0)
    assert new_p2 == FreeCAD.Vector(9, 0, 0)
    # vertical line with negative value
    p2 = FreeCAD.Vector(0, 10, 0)
    new_p1, new_p2 = osafe_funcs.extend_two_points(p1, p2, -1)
    assert new_p1 == FreeCAD.Vector(0, 1, 0)
    assert new_p2 == FreeCAD.Vector(0, 9, 0)

def test_get_right_wires_from_left_wire():
    cover = 75
    x1 = 0
    x2 = 2000
    x3 = 3000
    x4 = 5000
    y1 = 0
    y2 = 300
    y3 = 1000
    p1 = FreeCAD.Vector(x1, y1, 0)
    p2 = FreeCAD.Vector(x4, y1, 0)
    p3 = FreeCAD.Vector(x4, y3, 0)
    p4 = FreeCAD.Vector(x1, y3, 0)
    p5 = FreeCAD.Vector(x2, y1, 0)
    p6 = FreeCAD.Vector(x2, y2, 0)
    p7 = FreeCAD.Vector(x3, y2, 0)
    p8 = FreeCAD.Vector(x3, y1, 0)
    points = [p1, p2, p3, p4, p1]
    face = Part.Face(Part.makePolygon(points))
    points = [p1, p5, p6, p7, p8, p2, p3, p4, p1]
    face_2 = Part.Face(Part.makePolygon(points))
    p11 = FreeCAD.Vector(0, y3 - cover, 0)
    p22 = FreeCAD.Vector(x4, y3 - cover, 0)
    left_wire = Part.Wire(Part.makeLine(p11, p22))
    for number_of_wires in range(2, 20):
        distance = (y3 - 2 * cover) / (number_of_wires - 1)
        # Without Face
        right_wires = osafe_funcs.get_right_wires_from_left_wire(left_wire, number_of_wires, distance)
        assert len(right_wires) == number_of_wires
        # With Face
        right_wires = osafe_funcs.get_right_wires_from_left_wire(left_wire, number_of_wires, distance, face)
        assert len(right_wires) == number_of_wires
        # Face with opening
        right_wires = osafe_funcs.get_right_wires_from_left_wire(left_wire, number_of_wires, distance, face_2)
        assert len(right_wires) == number_of_wires + ((y2 - cover) // distance) + 1

def test_get_base_rebars_from_left_wire():
    cover = 75
    x1 = 0
    x2 = 2000
    x3 = 3000
    x4 = 5000
    y1 = 0
    y2 = 300
    y3 = 1000
    p1 = FreeCAD.Vector(x1, y1, 0)
    p2 = FreeCAD.Vector(x4, y1, 0)
    p3 = FreeCAD.Vector(x4, y3, 0)
    p4 = FreeCAD.Vector(x1, y3, 0)
    p5 = FreeCAD.Vector(x2, y1, 0)
    p6 = FreeCAD.Vector(x2, y2, 0)
    p7 = FreeCAD.Vector(x3, y2, 0)
    p8 = FreeCAD.Vector(x3, y1, 0)
    points = [p1, p2, p3, p4, p1]
    face = Part.Face(Part.makePolygon(points))
    points = [p1, p5, p6, p7, p8, p2, p3, p4, p1]
    face_2 = Part.Face(Part.makePolygon(points))
    p11 = FreeCAD.Vector(0, y3 - cover, 0)
    p22 = FreeCAD.Vector(x4, y3 - cover, 0)
    left_wire = Part.Wire(Part.makeLine(p11, p22))
    for number_of_rebars in range(2, 20):
        distance = (y3 - 2 * cover) / (number_of_rebars - 1)
        # Without Face
        right_wires = osafe_funcs.get_base_rebars_from_left_wire(left_wire, number_of_rebars, distance)
        assert len(right_wires) == number_of_rebars
        # With Face
        right_wires = osafe_funcs.get_base_rebars_from_left_wire(left_wire, number_of_rebars, distance, face)
        assert len(right_wires) == number_of_rebars
        # Face with opening
        right_wires = osafe_funcs.get_base_rebars_from_left_wire(left_wire, number_of_rebars, distance, face_2)
        assert len(right_wires) == number_of_rebars + ((y2 - cover) // distance) + 1

def test_get_top_bot_rebar_shapes_from_left_wire():
    foundation = document_rashidzadeh.Foundation
    strip = document_rashidzadeh.Strip009
    wire = strip.Base.Shape.Wires[0]
    top_rebars, bot_rebars, *_ = osafe_funcs.get_top_bot_rebar_shapes_from_left_wire(
        wire,
        number_of_top_rebars=6,
        number_of_bot_rebars=7,
        width=strip.width.Value,
        cut_shape=foundation.Shape,
        height=foundation.height.Value,
        cover=foundation.cover.Value,
    )
    assert len(top_rebars) == 4
    assert len(bot_rebars) == 4

def test_get_top_bot_rebar_shapes_from_strip_and_foundation():
    foundation = document_rashidzadeh.Foundation
    strip = document_rashidzadeh.Strip009
    top_rebars, bot_rebars, *_ = osafe_funcs.get_top_bot_rebar_shapes_from_strip_and_foundation(
        strip,
        number_of_top_rebars=6,
        number_of_bot_rebars=7,
        foundation=foundation,
        min_ratio_of_rebars=0,
    )
    assert len(top_rebars) == 6
    assert len(bot_rebars) == 7

def test_get_base_top_bot_rebar_from_left_wire():
    foundation = document_rashidzadeh.Foundation
    cut_shape = osafe_funcs.get_top_faces(foundation.Shape, fuse=True)
    strip = document_rashidzadeh.Strip009
    wire = strip.Base.Shape.Wires[0]
    number_of_top_rebars = 6
    number_of_bot_rebars = 6
    height = foundation.height.Value
    top_wires, bot_wires = osafe_funcs.get_base_top_bot_rebar_from_left_wire(
        wire,
        number_of_top_rebars=number_of_top_rebars,
        number_of_bot_rebars=number_of_bot_rebars,
        width=strip.width.Value,
        cut_shape=cut_shape,
        cover = foundation.cover.Value,
        height=height,
        top_rebar_diameter=20,
        bot_rebar_diameter=16,
        stirrup_diameter=12,
        extended=500,
    )
    assert len(top_wires) == 4
    assert len(bot_wires) == 4
    for wire in top_wires:
        for vertex in wire.Vertexes:
            assert cut_shape.isInside(FreeCAD.Vector(vertex.X, vertex.Y, vertex.Z), 0.1, True)
    for wire in bot_wires:
        for vertex in wire.Vertexes:
            assert cut_shape.isInside(FreeCAD.Vector(vertex.X, vertex.Y, vertex.Z), 0.1, True)

def test_get_centerline_of_rebars_from_wires():
    p1 = FreeCAD.Vector(-1000, -1000, 0)
    p2 = FreeCAD.Vector(1000, 1000, 0)
    p3 = FreeCAD.Vector(2000, 1000, 0)
    wire = Part.Wire(Part.makePolygon([p1, p2, p3]))
    rebars = osafe_funcs.get_centerline_of_rebars_from_wires(wires=[wire])
    assert len(rebars) == 1
    new_wire = rebars[0]
    bb = new_wire.BoundBox
    np.testing.assert_allclose(bb.ZLength, 310, atol=.01)
    np.testing.assert_allclose(bb.ZMax, -97, atol=.01)
    np.testing.assert_allclose(bb.ZMin, -407, atol=.01)
    # Bottom rebars
    wire = Part.Wire(Part.makePolygon([p1, p2, p3]))
    rebars = osafe_funcs.get_centerline_of_rebars_from_wires(wires=[wire], location="BOT")
    assert len(rebars) == 1
    new_wire = rebars[0]
    bb = new_wire.BoundBox
    np.testing.assert_allclose(bb.ZLength, 310, atol=.01)
    np.testing.assert_allclose(bb.ZMax, 407, atol=.01)
    np.testing.assert_allclose(bb.ZMin, 97, atol=.01)

def test_get_rebars_shapes_from_wires():
    lengths = range(100, 1000, 100)
    radiuses = range(10, 26, 2)
    for length, radius in zip(lengths, radiuses):
        p11 = FreeCAD.Vector(-1000, -1000, -length)
        p1 = FreeCAD.Vector(-1000, -1000, 0)
        p2 = FreeCAD.Vector(1000, 1000, 0)
        p3 = FreeCAD.Vector(2000, 1000, 0)
        p33 = FreeCAD.Vector(2000, 1000, -length)
        wire = Part.Wire(Part.makePolygon([p11, p1, p2, p3, p33]))
        rebars = osafe_funcs.get_rebars_shapes_from_wires(wires=[wire], radius=radius)
        assert len(rebars) == 1
        rebar = rebars[0]
        bb = rebar.BoundBox
        np.testing.assert_allclose(bb.ZLength, length + radius, atol=.01)
        np.testing.assert_allclose(bb.ZMax, radius, atol=.01)
        np.testing.assert_allclose(bb.ZMin, -length, atol=.01)

def test_get_centerline_of_rebars_from_left_wire():
    cover = 75
    x1 = 0
    x2 = 2000
    x3 = 3000
    x4 = 5000
    y1 = 0
    y2 = 300
    y3 = 1000
    p1 = FreeCAD.Vector(x1, y1, 0)
    p2 = FreeCAD.Vector(x4, y1, 0)
    p3 = FreeCAD.Vector(x4, y3, 0)
    p4 = FreeCAD.Vector(x1, y3, 0)
    p5 = FreeCAD.Vector(x2, y1, 0)
    p6 = FreeCAD.Vector(x2, y2, 0)
    p7 = FreeCAD.Vector(x3, y2, 0)
    p8 = FreeCAD.Vector(x3, y1, 0)
    points = [p1, p2, p3, p4, p1]
    face = Part.Face(Part.makePolygon(points))
    points = [p1, p5, p6, p7, p8, p2, p3, p4, p1]
    face_2 = Part.Face(Part.makePolygon(points))
    p11 = FreeCAD.Vector(0, y3 - cover, 0)
    p22 = FreeCAD.Vector(x4, y3 - cover, 0)
    left_wire = Part.Wire(Part.makeLine(p11, p22))
    for number_of_rebars in range(2, 20):
        distance = (y3 - 2 * cover) / (number_of_rebars - 1)
        # Without Face
        right_wires = osafe_funcs.get_centerline_of_rebars_from_left_wire(left_wire, number_of_rebars, distance)
        assert len(right_wires) == number_of_rebars
        # With Face
        right_wires = osafe_funcs.get_centerline_of_rebars_from_left_wire(left_wire, number_of_rebars, distance, face)
        assert len(right_wires) == number_of_rebars
        # Face with opening
        right_wires = osafe_funcs.get_centerline_of_rebars_from_left_wire(left_wire, number_of_rebars, distance, face_2)
        assert len(right_wires) == number_of_rebars + ((y2 - cover) // distance) + 1

def test_get_width_points():
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    w = .5
    points = osafe_funcs.get_width_points(p1, p2, w)
    assert len(points) == 4
    assert FreeCAD.Vector(0, -.5, 0) in points
    assert FreeCAD.Vector(0, .5, 0) in points
    assert FreeCAD.Vector(1, -.5, 0) in points
    assert FreeCAD.Vector(1, .5, 0) in points

def test_get_offset_points():
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    offset = .5
    points = osafe_funcs.get_offset_points(p1, p2, offset)
    assert len(points) == 2
    assert FreeCAD.Vector(0, .5, 0) in points
    assert FreeCAD.Vector(1, .5, 0) in points

def test_punch_area_edges():
    obj = document_rashidzadeh.Punch002
    d = obj.foundation.d.Value
    x = obj.bx + d
    y = obj.by + d
    offset_shape = osafe_funcs.rectangle_face(obj.center_of_load, x, y)
    foun_plan = obj.foundation.plan.copy()
    edges = osafe_funcs.punch_area_edges(foun_plan, offset_shape)
    assert len(edges) == 3

def test_punch_null_edges():
    punch = document_khalaji.Punch001
    null_edges, common_edges = osafe_funcs.punch_null_edges(punch)
    assert null_edges == ['Yes', 'No', 'Yes', 'Yes', 'No', 'Yes']
    assert len(null_edges) == 6
    assert len(common_edges) == 6

def test_punch_null_points():
    punch = document_rashidzadeh.Punch001
    null_edges, null_points = osafe_funcs.punch_null_points(punch)
    assert null_edges == ['Yes', 'No', 'Yes', 'Yes', 'No', 'Yes']
    assert len(null_edges) == 6
    assert len(null_points) == 6

def test_get_continuous_edges():
    edges = [b.Shape.Edges[0] for b in document_test.Beams.Group]
    edges_numbers = osafe_funcs.get_continuous_edges(edges)
    assert edges_numbers == [[13, 14, 15], [16, 1, 2, 3], [4, 5, 6], [8, 7], [10, 9], [12, 11]]

def test_get_continuous_edges_p():
    edges = [b.Shape.Edges[0] for b in document_test.Beams.Group]
    edges_numbers = osafe_funcs.get_continuous_edges_p(edges)
    assert edges_numbers == [[13, 14, 15], [16, 1, 2, 3], [4, 5, 6], [8, 7], [10, 9], [12, 11]]

def test_is_close():
    edges = [b.Shape.Edges[0] for b in document_test.Beams.Group]
    assert osafe_funcs.is_close(edges[12], edges[13])
    assert not osafe_funcs.is_close(edges[12], edges[14])

def test_angle_between_two_edges():
    edges = [b.Shape.Edges[0] for b in document_test.Beams.Group]
    angle = osafe_funcs.angle_between_two_edges(edges[12], edges[13])
    np.testing.assert_allclose(angle, 159.38619076306847, atol= .1)

def test_get_almost_direction_of_edges_list():
    bf = document_rashidzadeh.BaseFoundation005
    edges = bf.Base.Shape.Edges
    direction = osafe_funcs.get_almost_direction_of_edges_list(edges)
    assert direction == 'x'

def test_get_continuous_slabs():
    slabs = document_rashidzadeh.Beams.Group
    slab_lists = osafe_funcs.get_continuous_slabs(slabs)
    assert len(slab_lists) == 10

def test_get_common_part_of_base_foundation():
    bfs = []
    for o in document_rashidzadeh.Objects:
        if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
            bfs.append(o)
    points_common_shape, base_name_common_shape = osafe_funcs.get_common_part_of_base_foundation(bfs)
    assert len(base_name_common_shape) == len(bfs)
    assert len(points_common_shape) == 17

def test_get_foundation_shape_from_base_foundations():
    doc = document_rashidzadeh
    bfs  = osafe_funcs.get_objects_of_type('BaseFoundation', doc)
    shape = osafe_funcs.get_foundation_shape_from_base_foundations(bfs, continuous_layer='B')

def test_get_foundation_shape_from_base_foundations_mat():
    doc = document_rashidzadeh
    bfs  = osafe_funcs.get_objects_of_type('BaseFoundation', doc)
    shape = osafe_funcs.get_foundation_shape_from_base_foundations(bfs, foundation_type='Mat')

def test_get_foundation_shape_from_base_foundations_with_slabs():
    doc = document_rashidzadeh
    bfs  = osafe_funcs.get_objects_of_type('BaseFoundation', doc)
    slabs  = osafe_funcs.get_objects_of_type('RectangularSlab', doc)
    shape = osafe_funcs.get_foundation_shape_from_base_foundations(bfs, slabs=slabs)

def test_get_coordinate_and_width_between():
    coords_width = osafe_funcs.get_coordinate_and_width_between(1, 10, .7, False)
    assert len(coords_width) == 12

def test_draw_strip_automatically_in_mat_foundation():
    doc = document_rashidzadeh
    doc.Foundation.foundation_type = 'Mat'
    doc.recompute()
    osafe_funcs.draw_strip_automatically_in_mat_foundation(doc.Foundation)

def test_draw_strip_from_base_foundation():
    bfs = osafe_funcs.get_objects_of_type("BaseFoundation", doc=document_rashidzadeh)
    i = j = 0
    strips = []
    for bf in bfs:
        strip, i, j = osafe_funcs.draw_strip_from_base_foundation(bf, i, j)
        strips.extend(strip)
    assert len(bfs) == len(strips)

def test_draw_strip_automatically_in_strip_foundation():
    bfs = osafe_funcs.get_objects_of_type("BaseFoundation", doc=document_rashidzadeh)
    a_strips, b_strips = osafe_funcs.draw_strip_automatically_in_strip_foundation(document_rashidzadeh.Foundation)
    assert len(bfs) == len(a_strips.Group) + len(b_strips.Group)
    a_strips, b_strips = osafe_funcs.draw_strip_automatically_in_strip_foundation(base_foundations=bfs)
    assert len(bfs) == len(a_strips.Group) + len(b_strips.Group)

def test_get_similar_edge_direction_in_common_points_from_edges():
    edges = [b.Shape.Edges[0] for b in document_test.Beams.Group]
    df = osafe_funcs.get_similar_edge_direction_in_common_points_from_edges(edges)

def test_get_objects_of_type():
    objs = osafe_funcs.get_objects_of_type('BaseFoundation', document_base_plate)
    assert len(objs) == 7

def test_get_beams():
    beams = osafe_funcs.get_beams(doc=document_base_plate)
    assert len(beams) == 1

def test_is_beam_shape_on_base_foundations_base():
    doc = document_base_plate
    beam = osafe_funcs.get_beams(doc)[0]
    base_foudndations = osafe_funcs.get_objects_of_type('BaseFoundation', doc)
    print(base_foudndations)
    ret = osafe_funcs.is_beam_shape_on_base_foundations_base(beam, base_foudndations)
    assert ret

def test_get_beams_in_doc_that_belogns_to_base_foundations():
    beams = osafe_funcs.get_beams_in_doc_that_belogns_to_base_foundations(doc=document_base_plate)
    assert len(beams) == 1

def test_get_total_length_of_shapes():
    x1 = 0
    x2 = 5000
    y1 = 0
    y2 = 1000
    p1 = FreeCAD.Vector(x1, y1, 0)
    p2 = FreeCAD.Vector(x2, y1, 0)
    p4 = FreeCAD.Vector(x1, y2, 0)
    p3 = FreeCAD.Vector(x2, y2, 0)
    points = [p1, p2, p3, p4, p1]
    face = Part.Face(Part.makePolygon(points))
    length = osafe_funcs.get_total_length_of_shapes([face])
    assert length == (x2 + y2) * 2

if __name__ == '__main__':
    # test_get_similar_edge_direction_in_common_points_from_edges()
    test_get_continuous_edges()