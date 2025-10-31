from typing import List, Union
import math

import numpy as np

import FreeCAD
import Part
import DraftGeomUtils
import Draft

from osafe_objects import strip

PART_TOLERANCE = 0.01
if 'mm' in FreeCAD.Units.Length.__str__():
    PART_TOLERANCE = 1
elif 'cm' in FreeCAD.Units.Length.__str__():
    PART_TOLERANCE = .1
elif 'm' in FreeCAD.Units.Length.__str__():
    PART_TOLERANCE = .01



def remove_obj(name: str) -> None:
    o = FreeCAD.ActiveDocument.getObject(name)
    if hasattr(o, "Base") and o.Base:
        remove_obj(o.Base.Name)
    if hasattr(o, "Tool") and o.Tool:
        remove_obj(o.Tool.Name)
    if hasattr(o, "Shapes") and o.Shapes:
        for sh in o.Shapes:
            remove_obj(sh.Name)
    FreeCAD.ActiveDocument.removeObject(name)


def rectangle_face(
    center: FreeCAD.Vector,
    bx: Union[float, int],
    by: Union[float, int],
    ):

    v1, v2, v3, v4 = rectangle_vertexes(center, bx, by)
    return Part.Face(Part.makePolygon([v1, v2, v3, v4, v1]))

def rectangle_vertexes(
                       center: FreeCAD.Vector,
                       bx: Union[float, int],
                       by: Union[float, int],
                       ):
    dx = bx / 2
    dy = by / 2
    v1 = center.add(FreeCAD.Vector(-dx, -dy, 0))
    v2 = center.add(FreeCAD.Vector(dx, -dy, 0))
    v3 = center.add(FreeCAD.Vector(dx, dy, 0))
    v4 = center.add(FreeCAD.Vector(-dx, dy, 0))
    return [v1, v2, v3, v4]

def punch_area_edges(
    sh1: Part.Shape,
    sh2: Part.Shape,
    ):
    cut = sh1.cut(sh2, PART_TOLERANCE)
    edges = []
    for e in cut.Edges:
        p1 = e.firstVertex().Point
        p2 = e.lastVertex().Point
        if sh2.isInside(p1, .1, True) and sh2.isInside(p2, .1, True):
            edges.append(e)
    return edges

def punch_null_edges(
    punch,
    ) -> tuple:
    d = punch.foundation.d.Value
    x = punch.bx + d
    y = punch.by + d
    edges = punch.edges.Edges
    offset_shape = rectangle_face(punch.center_of_load, x, y)
    foun_plan = punch.foundation.plan.copy()
    if punch.angle != 0:
            offset_shape.rotate(
                punch.center_of_load,
                FreeCAD.Vector(0, 0, 1),
                punch.angle.Value,
                )
    common = foun_plan.common(offset_shape)
    common_edges = Part.__sortEdges__(common.Edges)
    null_edges = []
    for e in common_edges:
        p1 = e.firstVertex().Point
        p2 = e.lastVertex().Point
        for e2 in edges:
            p3 = e2.firstVertex().Point
            p4 = e2.lastVertex().Point
            if (is_equal_two_points(p1, p3) and is_equal_two_points(p2, p4)) or \
                (is_equal_two_points(p1, p4) and is_equal_two_points(p2, p3)):
                null_edges.append('No')
                break
        else:
            null_edges.append('Yes')
    return null_edges, common_edges

def punch_null_points(
    punch,
    ) -> tuple:
    null_edges, common_edges = punch_null_edges(punch)
    null_points_in_general = get_sort_points(common_edges, sort_edges=False)
    null_points_in_local = []
    for point in null_points_in_general:
        null_points_in_local.append(point.sub(punch.center_of_column))
    return null_edges, null_points_in_local


def punch_faces(
    edges: List[Part.Edge],
    d: Union[float, int],
    ):
    faces = []
    for e in edges:
        face = e.extrude(FreeCAD.Vector(0, 0, -d))
        faces.append(face)
    return faces

def length_of_edges(
    edges: List[Part.Edge],
    ):
    length = 0
    for e in edges:
        length += e.Length
    return length

def area(
    faces: List[Part.Face],
    ):
    area = 0
    for f in faces:
        area += f.Area
    return area

def center_of_mass(
    faces: List[Part.Face],
    ) -> FreeCAD.Vector:
    '''
    gives faces and returns the center of mass coordinate
    '''
    sorat_x = 0
    sorat_y = 0
    sorat_z = 0
    makhraj = 0

    for f in faces:
        area = f.Area
        x = f.CenterOfMass.x
        y = f.CenterOfMass.y
        z = f.CenterOfMass.z
        sorat_x += area * x
        sorat_y += area * y
        sorat_z += area * z
        makhraj += area
    if makhraj == 0:
        return None
    return FreeCAD.Vector(sorat_x / makhraj, sorat_y / makhraj, sorat_z / makhraj)

def moment_inertia(
    faces: List[Part.Face],
    ):
    '''
    return rotational moment inertia of faces list Ixx, Iyy
    '''
    Ixx = 0
    Iyy = 0
    Ixy = 0
    com = center_of_mass(faces)
    if not com:
        return 0, 0, 0
    x_bar, y_bar, z_bar = com
    for f in faces:
        A = f.Area
        x = f.CenterOfMass.x
        y = f.CenterOfMass.y
        z = f.CenterOfMass.z
        ixx = f.MatrixOfInertia.A11
        iyy = f.MatrixOfInertia.A22
        dx = abs(x - x_bar)
        dy = abs(y - y_bar)
        # dz = z - z_bar
        normal = f.normalAt(0, 0)
        if normal.x:
            Ixx += ixx + A * dy ** 2
            Iyy += A * (dx ** 2)  # + dz ** 2)
        elif normal.y:
            Ixx += A * (dy ** 2)  # + dz ** 2)
            Iyy += iyy + A * dx ** 2
        Ixy += A * dx * dy
    return Ixx, Iyy, Ixy

def location_of_column(
    faces: List[Part.Face],
    ) -> str:

    faces_normals = {'x': [], 'y': []}
    for f in faces:
        normal = f.normalAt(0, 0)
        normal_x = normal.x
        normal_y = normal.y
        if normal_x:
            if not normal_x in faces_normals['x']:
                faces_normals['x'].append(normal_x)
        if normal_y:
            if not normal_y in faces_normals['y']:
                faces_normals['y'].append(normal_y)
    if not (faces_normals['x'] and faces_normals['y']):
        return None

    no_of_faces = len(faces_normals['x'] + faces_normals['y'])
    if no_of_faces == 2:
        signx = faces_normals['x'][0] > 0
        signy = faces_normals['y'][0] > 0
        if not signy:
            if not signx:
                return 'Corner 3'
            elif signx:
                return 'Corner 4'
        elif signy:
            if signx:
                return 'Corner 1'
            elif not signx:
                return 'Corner 2'
        else:
            return 'Corner'
    elif no_of_faces == 3:
        sumx = sum(faces_normals['x'])
        sumy = sum(faces_normals['y'])
        if sumx == 0:
            if sumy == -1:
                return 'Edge 3'
            elif sumy == 1:
                return 'Edge 1'
        elif sumy == 0:
            if sumx == 1:
                return 'Edge 4'
            elif sumx == -1:
                return 'Edge 2'
        else:
            return 'Edge'
    else:
        return 'Interior'


def allowable_stress(bx, by, location, fc, b0, d, ACI2019=False, phi_c=.75):
    alpha_ss = {'Interior': 40, 'edge': 30, 'corner': 20}
    b0d = b0 * d
    beta = bx / by
    if beta < 1:
        beta = by / bx
    if ACI2019:
        lambda_s = min(math.sqrt(2 / (1 + .004 * d)), 1)
    else:
        lambda_s = 1
    alpha_s = alpha_ss[location]
    one_way_shear_capacity = math.sqrt(fc) * b0d / 6 * phi_c * lambda_s
    Vc1 = one_way_shear_capacity * 2
    Vc2 = one_way_shear_capacity * (1 + 2 / beta)
    Vc3 = one_way_shear_capacity * (2 + alpha_s * d / b0) / 2
    Vc = min(Vc1, Vc2, Vc3)
    vc = Vc / (b0d)
    return vc

def gamma_v(
            bx: Union[float, int],
            by: Union[float, int],
            ) -> tuple:
    gamma_fx = 1 / (1 + (2 / 3) * math.sqrt(by / bx))
    gamma_fy = 1 / (1 + (2 / 3) * math.sqrt(bx / by))
    gamma_vx = 1 - gamma_fx
    gamma_vy = 1 - gamma_fy
    return (gamma_vx, gamma_vy)

def get_user_location_faces(
                            faces: List[Part.Face],
                            location: str,
                            ) -> List[Part.Face]:

    location_normals = {
            'Corner 3': [(0, -1, 0), (-1, 0, 0)],
            'Corner 4': [(0, -1, 0), (1, 0, 0)],
            'Corner 1': [(0, 1, 0), (1, 0, 0)],
            'Corner 2': [(0, 1, 0), (-1, 0, 0)],
            'Edge 3': [(0, -1, 0), (-1, 0, 0), (1, 0, 0)],
            'Edge 4': [(0, -1, 0), (1, 0, 0), (0, 1, 0)],
            'Edge 1': [(0, 1, 0), (1, 0, 0), (-1, 0, 0)],
            'Edge 2': [(0, 1, 0), (-1, 0, 0), (0, -1, 0)],
            'Interior': [(0, 1, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0)]
            }

    normals = location_normals[location]
    if len(normals) >= len(faces):
        return faces
    new_faces = []
    for f in faces:
        normal = tuple(f.normalAt(0, 0))
        if normal in normals:
            new_faces.append(f)
    return new_faces

def sort_vertex(coords):
    if len(coords) < 2:
        return coords
    from functools import reduce
    import operator
    center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
    return sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)

def is_equal_two_points(p1, p2, tol=.1):
    '''
    check if two points are equal with tolerance
    '''
    if isinstance(p1, Part.Vertex):
        p1 = p1.Point
    if isinstance(p2, Part.Vertex):
        p2 = p2.Point
    return p1.isEqual(p2, tol)

def get_sort_points(
    edges,
    vector=True,
    get_last=False,
    sort_edges=True,
    ):
    vectors = []
    if len(edges) == 1:
        for v in edges[0].Vertexes:
            vectors.append(FreeCAD.Vector(v.X, v.Y, v.Z))
        return vectors
    if sort_edges:
        edges = Part.__sortEdges__(edges)
    for e1, e2 in zip(edges[:-1], edges[1:]):
        p = get_common_vector_in_two_edges(e1, e2)
        vectors.append(p)
    # add first point
    e = edges[0]
    p1 = e.firstVertex().Point
    p = vectors[0]
    if is_equal_two_points(p, p1):
        p1 = e.lastVertex().Point
    vectors.insert(0, p1)
    if get_last:
        e = edges[-1]
        p2 = e.lastVertex().Point
        p = vectors[-1]
        if is_equal_two_points(p, p2):
            p2 = e.firstVertex().Point
        vectors.append(p2)

    if vector:
        return vectors
    else:
        return [Part.Vertex(v) for v in vectors]

def get_common_vector_in_two_edges(e1, e2, tol=1) -> FreeCAD.Vector:
    p1 = e1.firstVertex().Point
    p2 = e1.lastVertex().Point
    p3 = e2.firstVertex().Point
    p4 = e2.lastVertex().Point
    if is_equal_two_points(p2, p3, tol) or is_equal_two_points(p2, p4, tol):
        return FreeCAD.Vector(p2.x, p2.y, p2.z)
    else:
        return FreeCAD.Vector(p1.x, p1.y, p1.z)

def split_face_with_scales(
    face : Part.Face,
    scales : list = [.75, .5],
    ) -> list:
    from BOPTools.GeneralFuseResult import GeneralFuseResult
    s1 = face.copy().scale(scales[0])
    s2 = face.copy().scale(scales[1])
    center_of_mass = face.CenterOfMass
    tr1 = center_of_mass.sub(s1.CenterOfMass)
    s1.Placement.Base = tr1
    tr2 = center_of_mass.sub(s2.CenterOfMass)
    s2.Placement.Base = tr2
    area1 = face.cut(s1, PART_TOLERANCE)
    area2 = s1.cut(s2, PART_TOLERANCE)
    e1, e2 = sorted(face.Edges, key=lambda x: x.Length, reverse=True)[0:2]
    v1 = e1.CenterOfMass
    v2 = e2.CenterOfMass
    poly = Part.makePolygon([v1, center_of_mass, v2])
    faces = []
    for area in (area1, area2):
        pieces, map_ = area.generalFuse([poly])
        gr = GeneralFuseResult([area, poly], (pieces,map_))
        gr.splitAggregates()
        comp = Part.Compound(gr.pieces)
        faces.extend(comp.Faces)
    faces.append(Part.Face(s2))
    return faces

def get_sub_areas_points_from_face_with_scales(
    face : Part.Face,
    scales : list = [.75, .5],
    ) -> list:
    faces = split_face_with_scales(face, scales)
    faces_points = []
    for f in faces:
        points = get_sort_points(f.Edges)
        faces_points.append(points)
    return faces_points

def get_points_inside_base_foundations(
    base_foundations : list,
    ) -> dict:
    '''
    get base foundation objects and return the dictionary of points as key and
    base foundation name that point is inside them as values
    '''
    points = get_bf_points(base_foundations)
    d = {key: set() for key in points}
    for p in points:
        point = FreeCAD.Vector(p)
        for base in base_foundations:
            if base.plan.isInside(point, 1, True):
                d[p].add(base.Name)
    return d

def get_bf_points(bfs):
    points = set()
    for bf in bfs:
        for point in bf.Base.Points:
            points.add(tuple(point))
    return points

def get_line_equation(p1, p2):
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    if x1 == x2:
        return ''
    else:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return f'{m} * x + {b}'

def extend_two_points(
    p1 : FreeCAD.Vector,
    p2 : FreeCAD.Vector,
    length : float = 4000,
    ) -> tuple:
    xs = p1.x
    xe = p2.x
    ys = p1.y
    ye = p2.y
    delta_x = xe - xs
    d = p1.distanceToPoint(p2)
    if delta_x == 0:
        dx = 0
        dy = length
        new_start_point = p1.add(FreeCAD.Vector(dx, -dy, 0))
        new_d = new_start_point.distanceToPoint(p2)
        if length > 0:
            if new_d > d:
                new_end_point = p2.add(FreeCAD.Vector(dx, dy, 0))
            else:
                new_start_point = p1.add(FreeCAD.Vector(dx, dy, 0))
                new_end_point = p2.add(FreeCAD.Vector(dx, -dy, 0))
        else:
            if new_d < d:
                new_end_point = p2.add(FreeCAD.Vector(dx, dy, 0))
            else:
                new_start_point = p1.add(FreeCAD.Vector(dx, dy, 0))
                new_end_point = p2.add(FreeCAD.Vector(dx, -dy, 0))
    else:
        equation = get_line_equation(p1, p2)
        m = (ye - ys) / (xe - xs)
        dx = length / math.sqrt(1 + m ** 2)
        x = p2.x + dx
        y = eval(equation)
        dist = math.sqrt((x - p1.x) ** 2 + 
                        (y - p1.y) ** 2)
        if length < 0:
            dx *= -1
        if dist > d:
            new_end_point = FreeCAD.Vector(x, y, p2.z)
            x = p1.x - dx
            y = eval(equation)
            new_start_point = FreeCAD.Vector(x, y, p1.z)
        else:
            x = p2.x - dx
            y = eval(equation)
            new_end_point = FreeCAD.Vector(x, y, p2.z)
            x = p1.x + dx
            y = eval(equation)
            new_start_point = FreeCAD.Vector(x, y, p1.z)
    return new_start_point, new_end_point

def get_width_points(
    p1 : FreeCAD.Vector,
    p2 : FreeCAD.Vector,
    width : float,
    teta : Union[float, None] = None,
    ) -> list:
    xs, ys, xe, ye, z = p1.x, p1.y, p2.x, p2.y, p1.z
    if teta is None:
        v = p2 - p1
        teta = math.atan2(v.y, v.x)
    points = []
    _sin = math.sin(teta)
    _cos = math.cos(teta)
    x = xs - width * _sin
    y = ys + width * _cos
    points.append(FreeCAD.Vector(x, y, z))
    x = xs + width * _sin
    y = ys - width * _cos
    points.append(FreeCAD.Vector(x, y, z))
    x = xe + width * _sin
    y = ye - width * _cos
    points.append(FreeCAD.Vector(x, y, z))
    x = xe - width * _sin
    y = ye + width * _cos
    points.append(FreeCAD.Vector(x, y, z))
    return points

def get_offset_points(
    p1 : FreeCAD.Vector,
    p2 : FreeCAD.Vector,
    offset : float,
    ) -> tuple:
    if offset == 0:
        return p1, p2
    else:
        x1 = p1.x
        y1 = p1.y
        x2 = p2.x
        y2 = p2.y
        neg = False if offset >= 0 else True
        distance = abs(offset)
        x1, y1, x2, y2 = offset_frame_points(x1, y1, x2, y2, distance, neg)
        new_start_point = FreeCAD.Vector(x1, y1, p1.z)
        new_end_point = FreeCAD.Vector(x2, y2, p2.z)
        return new_start_point, new_end_point

def offset_frame_points(x1, y1, x2, y2, distance, neg:bool):
    if x2 == x1:
        dy = 0
        dx = distance
    else:
        import math
        m = (y2 - y1) / (x2 - x1)
        dy = distance / math.sqrt(1 + m ** 2)
        dx = m * dy
    if neg:
        dx *= -1
        dy *= -1
    x1_offset = x1 - dx
    x2_offset = x2 - dx
    y1_offset = y1 + dy
    y2_offset = y2 + dy
    return x1_offset, y1_offset, x2_offset, y2_offset

def get_common_part_of_base_foundation(base_foundations):
    if len(base_foundations) < 2:
        return {}, {}
    points_base_connections = get_points_inside_base_foundations(base_foundations)
    points_common_shape = {}
    base_name_common_shape = {}
    for point, names in points_base_connections.items():
        if len(names) > 1:
            bases = [FreeCAD.ActiveDocument.getObject(name) for name in names]
            comm = bases[0].extended_shape
            for base in bases[1:]:
                comm = comm.common(base.extended_shape)
            points_common_shape[point] = comm
            for name in names:
                commons = base_name_common_shape.get(name, None)
                if commons is None:
                    base_name_common_shape[name] = [comm]
                else:
                    base_name_common_shape[name].append(comm)
    return points_common_shape, base_name_common_shape

def get_top_faces(
        shape,
        fuse : bool = False,
        tol : float = 0,
        remove_colinear_edge: bool=False,
        ):
    z_max = shape.BoundBox.ZMax
    faces = []
    for f in shape.Faces:
        if math.isclose(f.BoundBox.ZLength, 0, abs_tol=0.1) and math.isclose(f.BoundBox.ZMax, z_max, abs_tol=0.1):
            if remove_colinear_edge:
                f = remove_colinear_edges(f, tol)
            faces.append(f)
    if fuse:
        if len(faces) > 1:
            face = faces[0].fuse(faces[1:], PART_TOLERANCE)
            face = face.removeSplitter()
        else:
            face = faces[0]
        # face = remove_colinear_edges(face, tol)
        return face
    return faces

def get_foundation_shape_from_base_foundations(
        base_foundations,
        height : float = 0,
        foundation_type : str = 'Strip',
        continuous_layer : str = 'A',
        openings : list = [],
        split_mat : bool = True,
        slabs : list = [],
        tol : float = 0,
        ):
    '''
    Creates Foundation shapes from base foundations objects. if height is 0, the height of each base foundations
    used to create foundation shape
    continuoues_dir : in Strip foundation, the strips with layer name equals to continuoues_dir get
        continuoes and other side cut with this shapes
    tol: for remove colineare lines from face of foundation
    '''
    shapes = []
    outer_wire = Part.Shape()
    plan_without_openings = Part.Shape()
    if base_foundations:
        if height == 0:
            heights = [base_foundation.height.Value for base_foundation in base_foundations]
        else:
            heights = [height] * len(base_foundations)
        openings_shapes = [o.Shape for o in openings]
        points_common_shape, base_name_common_shape = get_common_part_of_base_foundation(base_foundations)
        used_commons_center_point = []
        for base_foundation, height in zip(base_foundations, heights):
            shape = get_continuous_base_foundation_shape(
                    base_foundation,
                    points_common_shape,
                    height,
                    )
            if foundation_type == 'Strip' and \
                continuous_layer != 'AB' and \
                base_foundation.layer != continuous_layer:
                commons = base_name_common_shape.get(base_foundation.Name, None)
                unused_common = []
                if commons:
                    for comm in commons:
                        for p in used_commons_center_point:
                            if is_equal_two_points(comm.BoundBox.Center, p, 1):
                                break
                        else:
                            used_commons_center_point.append(comm.BoundBox.Center)
                            unused_common.append(comm)
                    commons = [comm.extrude(FreeCAD.Vector(0, 0, -height)) for comm in unused_common]
                    shape = shape.cut(commons, PART_TOLERANCE)
            if foundation_type == 'Strip' and openings:
                shape = shape.cut(openings_shapes, PART_TOLERANCE)
            shapes.append(shape)
            if foundation_type == 'Strip':
                base_foundation.extended_plan = Part.makeCompound(get_top_faces(shape, tol=tol))
    if foundation_type == 'Strip' and slabs:
        slabs_a = [slab.Shape for slab in slabs if slab.layer == 'A']
        slabs_b = [slab.Shape for slab in slabs if slab.layer == 'B']
        comp_a = Part.makeCompound(slabs_a)
        comp_b = Part.makeCompound(slabs_b)
        if continuous_layer != 'AB' and slabs_a and slabs_b:
            if continuous_layer == 'A':
                diff = comp_b.cut(comp_a, PART_TOLERANCE)
                shape = Part.makeCompound([comp_a, diff])
            elif continuous_layer == 'B':
                diff = comp_a.cut(comp_b, PART_TOLERANCE)
                shape = Part.makeCompound([comp_b, diff])
            shapes.append(shape)
        else:
            shapes.append(comp_a)
            shapes.append(comp_b)
    if len(shapes) > 1:
        strip_shape = shapes[0].fuse(shapes[1:], PART_TOLERANCE)
        strip_shape = strip_shape.removeSplitter()
    else:
        strip_shape = shapes[0]
    if foundation_type == 'Strip':
        shape = Part.makeCompound(shapes)
        plan = get_top_faces(strip_shape, fuse=True, tol=tol, remove_colinear_edge=False)
    elif foundation_type == 'Mat':
        if height == 0:
            from collections import Counter
            counts = Counter(heights)
            height = counts.most_common[0][0]
        outer_wire = get_top_faces(strip_shape, fuse=True, tol=tol).OuterWire
        plan_without_openings = Part.Face(outer_wire)
        if split_mat:
            faces = split_face_with_scales(plan_without_openings)
            shapes = []
            for face in faces:
                shape = face.extrude(FreeCAD.Vector(0, 0, -height))
                if openings:
                    shape = shape.cut(openings_shapes, PART_TOLERANCE)
                shapes.append(shape)
            shape = Part.makeCompound(shapes)
        else:
            shape = plan_without_openings.extrude(FreeCAD.Vector(0, 0, -height))
            if openings:
                shape = shape.cut(openings_shapes, PART_TOLERANCE)
        plan = get_top_faces(shape, fuse=True, tol=tol)
    if slabs:
        mat_slabs_shapes = [slab.Shape for slab in slabs if not hasattr(slab, 'layer')]
        if mat_slabs_shapes:
            shape = shape.fuse(mat_slabs_shapes, PART_TOLERANCE)
            shape = shape.removeSplitter()
    return shape, outer_wire, plan, plan_without_openings

def get_continuous_base_foundation_shape(
        base_foundation,
        points_common_shape,
        height : float,
        ):
    '''
    This function gets the one base of foundation object, common shapes with
    other of base foundations and return a solid shape
    '''

    def get_cut_faces(sh1, sh2):
        cut = sh1.cut(sh2, PART_TOLERANCE)
        if len(cut.Faces) > 1:
            faces = cut.Faces
            areas = [f.Area for f in faces]
            i = areas.index(max(areas))
            faces.remove(faces[i])
            return faces
        else:
            return None

    shapes = []
    cut_shape = []
    
    first_point = tuple(base_foundation.Base.Start)
    last_point = tuple(base_foundation.Base.End)
    comm = points_common_shape.get(first_point, None)
    if comm is not None:
        shapes.append(comm)
        faces = get_cut_faces(base_foundation.plan, comm)
        if faces is not None:
            cut_shape.extend(faces)
        for e in comm.Edges:
            intersection = DraftGeomUtils.findIntersection(
                e,
                base_foundation.extended_first_edge,
                )
            if intersection:
                try:
                    base_foundation.first_edge = \
                        Part.makeLine(
                            intersection[0], FreeCAD.Vector(*first_point))
                    break
                except Part.OCCError:
                    continue
    comm = points_common_shape.get(last_point, None)
    if comm is not None:
        shapes.append(comm)
        faces = get_cut_faces(base_foundation.plan, comm)
        if faces is not None:
            cut_shape.extend(faces)
        for e in comm.Edges:
            intersection = DraftGeomUtils.findIntersection(
                e,
                base_foundation.extended_last_edge,
                )
            if intersection:
                try:
                    base_foundation.last_edge = \
                        Part.makeLine(
                            FreeCAD.Vector(*last_point), intersection[0]
                                )
                    break
                except Part.OCCError:
                    continue
    shapes.append(base_foundation.plan)
    shapes = [shape.extrude(FreeCAD.Vector(0, 0, -height)) for shape in shapes]
    if len(shapes) > 1:
        shape = shapes[0].fuse(shapes[1:], PART_TOLERANCE)
        shape = shape.removeSplitter()
    else:
        shape = shapes[0]
    if cut_shape:
        cut_shape = [shape.extrude(FreeCAD.Vector(0, 0, -height)) for shape in cut_shape]
        shape = shape.cut(cut_shape, PART_TOLERANCE)
    return shape

def get_common_part_of_strips(points, offset, width):
    '''
    getting a series of points that create a polyline with width and
    then return the common part of all lines with width equal to width
    '''
    if len(points) < 3:
        return []
    commons = []
    for i, p in enumerate(points[1:-1]):
        new_points = points[i: i + 3]
        shapes = []
        for j, (p1, p2) in enumerate(zip(new_points[:-1], new_points[1:])):
            if j == 0:
                _, p2 = extend_two_points(p1, p2)
            elif j == 1:
                p1, _ = extend_two_points(p1, p2)
            p1, p2 = get_offset_points(p1, p2, offset)
            rectangle_points = get_width_points(p1, p2, width)
            rectangle_points.append(rectangle_points[0])
            shapes.append(Part.Face(Part.makePolygon(rectangle_points)))
        comm = shapes[0]
        for sh in shapes[1:]:
            comm = comm.common(sh)
        commons.append(comm)
    return commons

def make_base_foundation_shape_from_beams(
        beams : list,
        left_width : float,
        right_width : float,
        ) -> tuple:
    '''
    get a list of beams and create the shape of strip
    return shape of strip, left_wire, right_wire
    '''
    es = [b.Shape.Edges[0] for b in beams]
    wire = get_wire_with_sorted_points(es)
    sh, wl, wr = get_left_right_offset_wire_and_shape(wire, left_width, right_width)
    return sh, wire, wl, wr

def get_left_right_offset_wire_and_shape(wire, left_width, right_width):
    normal = FreeCAD.Vector(0, 0, 1)
    dvec = DraftGeomUtils.vec(wire.Edges[0]).cross(normal)
    dvec.normalize()
    dvec.multiply(right_width)
    right_wire = DraftGeomUtils.offsetWire(wire,dvec)
    right_wire = remove_null_edges_from_wire(right_wire)
    dvec = DraftGeomUtils.vec(wire.Edges[0]).cross(normal)
    dvec.normalize()
    dvec = dvec.negative()
    dvec.multiply(left_width)
    left_wire = DraftGeomUtils.offsetWire(wire,dvec)
    left_wire = remove_null_edges_from_wire(left_wire)
    shape = DraftGeomUtils.bind(left_wire, right_wire)
    return shape, left_wire, right_wire

def get_extended_wire_first_last_edge(wire, length=4000):
    '''
    return the first and last edges with length equal to length that elongation wire
    '''
    start_edge = wire.Edges[0]
    end_edge = wire.Edges[-1]
    if len(wire.Edges) == 1:
        v1, v4 = start_edge.Vertexes
        p1 = v1.Point
        p4 = v4.Point
        p11, p22 = extend_two_points(p1, p4, length)
        if length < 0:
            e = Part.makeLine(p11, p22)
            return e, e
    else:
        v1 = start_edge.firstVertex()
        v2 = start_edge.lastVertex()
        p1 = v1.Point
        p2 = v2.Point
        p11, _ = extend_two_points(p1, p2, length)
        v3 = end_edge.firstVertex()
        v4 = end_edge.lastVertex()
        p3 = v3.Point
        p4 = v4.Point
        _, p22 = extend_two_points(p3, p4, length)
    if length < 0:
        e1 = Part.makeLine(p11, p2)
        e2 = Part.makeLine(p3, p22)
    else:
        e1 = Part.makeLine(p11, p1)
        e2 = Part.makeLine(p4, p22)
    return e1, e2

def get_extended_wire(wire, length=2000):
    e1, e2 = get_extended_wire_first_last_edge(wire, length)
    if length < 0:
        if len(wire.Edges) == 1:
            edges = [e1]
        else:
            edges = [e1] + wire.Edges[1:-1] + [e2]
    else:
        edges = [e1] + wire.Edges + [e2]
    wire = Part.Wire(edges)
    return wire, e1, e2

def  get_right_wires_from_left_wire(
        wire: Part.Shape,
        number_of_wires: int,
        distance: float,
        cut_shape: Part.Shape=None,
        extended: float= 0,
        ):
    '''
    get a wire, and return the number_of_wires Wire in the right of wire
    with distances of distance
    cut_shape: Top cut_shape of foundation or frame
    '''
    normal = FreeCAD.Vector(0, 0, 1)
    dvec = DraftGeomUtils.vec(wire.Edges[0]).cross(normal)
    if extended != 0:
        wire, *_ = get_extended_wire(wire, extended)
    wires = [wire]
    for i in range(1, number_of_wires):
        dvec.normalize()
        dvec.multiply(i * distance)
        right_wire = DraftGeomUtils.offsetWire(wire, dvec)
        right_wire = remove_null_edges_from_wire(right_wire)
        wires.append(right_wire)
    if cut_shape is not None:
        wires_shape = Part.makeCompound(wires)
        dz = cut_shape.BoundBox.Center.z - wires_shape.BoundBox.Center.z
        wires_shape = wires_shape.translate(FreeCAD.Vector(0, 0, dz))
        com = cut_shape.common(wires_shape)
        com = com.translate(FreeCAD.Vector(0, 0, -dz))
        wires = com.Wires
    return wires
    
def get_base_rebars_from_left_wire(
        wire: Part.Shape,
        number_of_rebars: int,
        distance: float,
        cut_shape: Part.Shape=None,
        cover: float=75,
        rebar_diameter: int=20,
        extended: float= 0,
        ):
    '''
    get a wire, and return the number_of_rebars Wire in the right of wire
    with distances of distance
    cut_shape: cut_shape to cut base rebars with it
    '''
    radius = rebar_diameter / 2
    wires = get_right_wires_from_left_wire(wire, number_of_rebars, distance, cut_shape, extended)
    base_rebars = []
    for wire in wires:
        wire, *_ = get_extended_wire(wire, -(cover + radius))
        base_rebars.append(wire)
    return base_rebars

def get_centerline_of_rebars_from_left_wire(
        wire: Part.Shape,
        number_of_rebars: int,
        spacing: float,
        cut_shape: Part.Shape=None,
        cover: float=75,
        diameter: int=20,
        stirrup_diameter: int=12,
        factor_after_arc: float=16,
        rebars_location: str='TOP', # 'BOT'
        rounding: float=3,
        extended: float=0,
        ) -> list:
    '''
    get a wire, and return the number_of_rebars Wire in the right of wire
    with spaces of spacing
    cut_shape: cut_shape to cut with base wires with it
    diameter: diameter of rebar
    factor_after_arc: multiply to diameter of rebar, for example 16 * db
    '''
    wires = get_base_rebars_from_left_wire(wire, number_of_rebars, spacing, cut_shape, cover, diameter, extended)
    radius = diameter / 2
    new_wires = []
    for wire in wires:
        sign = -1 if rebars_location == 'TOP' else 1
        wire = wire.translate(FreeCAD.Vector(0, 0, sign * (cover + stirrup_diameter + radius)))
        v1 = wire.Vertexes[0]
        v2 = wire.Vertexes[-1]
        v1 = v1.Point
        v2 = v2.Point
        elongation = (sign * (factor_after_arc * diameter - radius))
        v11 = FreeCAD.Vector(v1.x, v1.y, v1.z + elongation)
        v22 = FreeCAD.Vector(v2.x, v2.y, v2.z + elongation)
        e1 = Part.makeLine(v11, v1)
        e2 = Part.makeLine(v22, v2)
        edges = [e1] + wire.Edges + [e2]
        new_wire = Part.Wire(edges)
        new_wire = DraftGeomUtils.filletWire(new_wire, rounding * radius)
        new_wires.append(new_wire)
    return new_wires

def get_base_top_bot_rebar_from_left_wire(
        wire: Part.Shape,
        number_of_top_rebars: int,
        number_of_bot_rebars: int,
        width: float,
        cut_shape: Part.Shape,
        cover: float,
        height: float,
        top_rebar_diameter: int=20,
        bot_rebar_diameter: int=20,
        stirrup_diameter: int=12,
        extended: float=0,
        ):
    '''
    get a wire, and return the top and bottom of wires in foundation
    '''
    top_spacing = (width - 2 * (cover + stirrup_diameter) - top_rebar_diameter) / (number_of_top_rebars - 1)
    top_wires = get_base_rebars_from_left_wire(
        wire,
        number_of_top_rebars,
        top_spacing,
        cut_shape,
        cover,
        top_rebar_diameter,
        extended)
    if number_of_top_rebars == number_of_bot_rebars and top_rebar_diameter == bot_rebar_diameter:
        bot_wires = []
        for w in top_wires:
            w = w.copy()
            w = w.translate(FreeCAD.Vector(0, 0, -height))
            bot_wires.append(w)
    else:
        wire = wire.copy()
        wire = wire.translate(FreeCAD.Vector(0, 0, -height))
        bot_spacing = (width - 2 * (cover + stirrup_diameter) - bot_rebar_diameter) / (number_of_bot_rebars - 1)
        bot_wires = get_base_rebars_from_left_wire(
            wire,
            number_of_bot_rebars,
            bot_spacing,
            cut_shape,
            cover,
            top_rebar_diameter,
            extended)
    return top_wires, bot_wires

def get_centerline_of_rebars_from_wires(
        wires: List[Part.Shape],
        cover: float=75,
        diameter: int=20,
        stirrup_diameter: int=12,
        rounding: float=3,
        factor_after_arc: float=16,
        location: str="TOP",
        ):
    '''
    get a wire, and return the centerline of rebars
    '''
    sign = -1 if location == 'TOP' else 1
    new_wires = []
    radius = diameter / 2
    for wire in wires:
        wire = wire.translate(FreeCAD.Vector(0, 0,  sign * (cover + stirrup_diameter + radius)))
        v1 = wire.Vertexes[0]
        v2 = wire.Vertexes[-1]
        v1 = v1.Point
        v2 = v2.Point
        elongation = (sign * (factor_after_arc * diameter - radius))
        v11 = FreeCAD.Vector(v1.x, v1.y, v1.z + elongation)
        v22 = FreeCAD.Vector(v2.x, v2.y, v2.z + elongation)
        e1 = Part.makeLine(v11, v1)
        e2 = Part.makeLine(v22, v2)
        edges = [e1] + wire.Edges + [e2]
        new_wire = Part.Wire(edges)
        new_wire = DraftGeomUtils.filletWire(new_wire, rounding * diameter)
        new_wires.append(new_wire)
    return new_wires
    
def get_centerline_of_top_bot_rebars_from_wires(
        top_wires: List[Part.Shape],
        bot_wires: List[Part.Shape],
        cover: float=75,
        top_diameter: int=20,
        bot_diameter: int=20,
        stirrup_diameter: int=12,
        rounding: float=3,
        factor_after_arc: float=16,
        ):
    '''
    get a wire, and return the top and bottom centerline of rebars
    '''
    top_rebars = get_centerline_of_rebars_from_wires(
        top_wires,
        cover,
        top_diameter,
        stirrup_diameter,
        rounding,
        factor_after_arc,
        location='TOP',
        )
    bot_rebars = get_centerline_of_rebars_from_wires(
        bot_wires,
        cover,
        bot_diameter,
        stirrup_diameter,
        rounding,
        factor_after_arc,
        location='BOT',
        )
    return top_rebars, bot_rebars

def get_rebars_shapes_from_wires(
        wires: Union[Part.Shape],
        radius: float,
):
    shapes = []
    for wire in wires:
        bpoint, bvec = get_base_and_axis(wire)
        if not bpoint:
            return
        circle = Part.makeCircle(radius, bpoint, bvec)
        circle = Part.Wire(circle)
        try:
            bar = wire.makePipeShell([circle], True, False, 2)
            shapes.append(bar)
        except Part.OCCError:
            print("Arch: error sweeping rebar profile along the base sketch")
            continue
    return shapes

def get_base_and_axis(wire):
    "returns a base point and orientation axis from the base wire"
    e = wire.Edges[0]
    v = e.tangentAt(e.FirstParameter)
    return e.Vertexes[0].Point,v

def get_top_bot_rebar_shapes_from_left_wire(
        wire: Part.Shape,
        number_of_top_rebars: int,
        number_of_bot_rebars: int,
        width: float,
        cut_shape: Part.Shape,
        height: float,
        cover: float=75,
        top_rebar_diameter: int=20,
        bot_rebar_diameter: int=20,
        stirrup_diameter: int=12,
        extended: float=0,
        rounding: float=3,
        factor_after_arc: float=16,
        ):
    '''
    get a wire, and return the top and bottom  rebar shapes
    '''
    top_wires, bot_wires = get_base_top_bot_rebar_from_left_wire(
        wire,
        number_of_top_rebars,
        number_of_bot_rebars,
        width,
        cut_shape,
        cover,
        height,
        top_rebar_diameter,
        bot_rebar_diameter,
        stirrup_diameter,
        extended,
    )
    top_wires, bot_wires = get_centerline_of_top_bot_rebars_from_wires(
        top_wires=top_wires,
        bot_wires=bot_wires,
        cover=cover,
        top_diameter=top_rebar_diameter,
        bot_diameter=bot_rebar_diameter,
        stirrup_diameter=stirrup_diameter,
        rounding=rounding,
        factor_after_arc=factor_after_arc,
    )
    top_rebar_shapes = get_rebars_shapes_from_wires(top_wires, top_rebar_diameter / 2)
    bot_rebar_shapes = get_rebars_shapes_from_wires(bot_wires, bot_rebar_diameter / 2)
    return top_rebar_shapes, bot_rebar_shapes, top_wires, bot_wires

def get_left_wire_from_strip(strip, cover=0):
    main_wire = strip.Base.Shape.copy()
    normal = FreeCAD.Vector(0, 0, 1)
    dvec = DraftGeomUtils.vec(main_wire.Edges[0]).cross(normal)
    dvec.normalize()
    dvec = dvec.negative()
    dvec.multiply(strip.left_width.Value - cover)
    left_wire = DraftGeomUtils.offsetWire(main_wire,dvec)
    left_wire = remove_null_edges_from_wire(left_wire)
    return left_wire

def get_top_bot_rebar_shapes_from_strip_and_foundation(
        strip,
        top_rebar_diameter: int=20,
        bot_rebar_diameter: int=20,
        number_of_top_rebars: int=0,
        number_of_bot_rebars: int=0,
        width: float=0,
        height: float=0,
        cover: float=0,
        stirrup_diameter: int=12,
        foundation=None,
        cut_shape: Union[Part.Shape, None]=None,
        rounding: float=3,
        factor_after_arc: float=16,
        extended: float=0,
        min_ratio_of_rebars: float=0.0018,
        ):
    # Get left wire of strip
    # get width
    if width == 0:
        width = strip.width.Value
    if height == 0:
        height = foundation.height.Value
    if cover == 0:
        cover = foundation.cover.Value
    if cut_shape is None:
        cut_shape = foundation.Shape.copy()
    dist_from_left = cover + stirrup_diameter + max(top_rebar_diameter, bot_rebar_diameter)
    left_wire = get_left_wire_from_strip(strip, dist_from_left)
    if min_ratio_of_rebars != 0:
        as_min = min_ratio_of_rebars * height * width
        as_top_rebar = math.pi * top_rebar_diameter ** 2 / 4
        number_of_top_rebars_min = int((as_min // as_top_rebar) + 1 )
        as_bot_rebar = math.pi * bot_rebar_diameter ** 2 / 4
        number_of_bot_rebars_min = int((as_min // as_bot_rebar) + 1 )
        number_of_top_rebars = max(number_of_top_rebars, number_of_top_rebars_min)
        number_of_bot_rebars = max(number_of_bot_rebars, number_of_bot_rebars_min)
    top_rebar_shapes, bot_rebar_shapes, top_wires, bot_wires = get_top_bot_rebar_shapes_from_left_wire(
        left_wire,
        number_of_top_rebars,
        number_of_bot_rebars,
        width,
        cut_shape,
        height,
        cover,
        top_rebar_diameter,
        bot_rebar_diameter,
        stirrup_diameter,
        extended,
        rounding,
        factor_after_arc,
        )
    return top_rebar_shapes, bot_rebar_shapes, top_wires, bot_wires
        
def remove_null_edges_from_wire(w):
    es = []
    for e in w.Edges:
        if len(e.Vertexes) == 2:
            es.append(e)
    return Part.Wire(es)

def get_sort_points_from_slabs(slabs : list) -> list:
    edges = [s.Shape.Edges[0] for s in slabs]
    continuous_points = get_sort_points(edges, get_last=True)
    return continuous_points

def get_wire_with_sorted_points(edges):
    if type(edges) == Part.Wire:
        edges = edges.Edges
    sorted_points = get_sort_points(edges, get_last=True)
    edges = []
    for p1, p2 in zip(sorted_points[:-1], sorted_points[1:]):
        edge = Part.makeLine(p1, p2)
        edges.append(edge)
    return Part.Wire(edges)

def get_almost_direction_of_edges_list(edges : list) -> str:
    '''This functions give a list of edges and 
        recognize direction of each edge and return
        x if most of edges are in x direction, otherwise y'''
    x_weight = 0
    y_weight = 0
    for edge in edges:
        v = edge.tangentAt(0)
        x_weight += abs(v.x) 
        y_weight += abs(v.y)
    if x_weight > y_weight:
        return 'x'
    return 'y'

def make_automatic_base_foundation(
        beams,
        width,
        x_stirp_name : str = 'A',
        y_stirp_name : str = 'B',
        angle : int = 45,
        height : int = 1000,
        soil_modulus : str='2',
        ):
    from osafe_objects.base_foundation import make_base_foundation
    continuous_slabs = get_continuous_slabs(beams, angle)
    strips = []
    for slabs in continuous_slabs:
        edges = [slab.Shape.Edges[0] for slab in slabs]
        edges_group = Part.sortEdges(edges)
        for edges in edges_group:
            strip_direction = get_almost_direction_of_edges_list(edges)
            if strip_direction == 'x':
                layer = x_stirp_name
            else:
                layer = y_stirp_name
            points = get_sort_points(edges, get_last=True, sort_edges=True)
            wire = Draft.make_wire(points, face=False)
            strip = make_base_foundation(wire, layer, width, height, soil_modulus)
            strips.append(strip)
    for beam in beams:
        # FreeCAD.ActiveDocument.removeObject(beam.Name)
        beam.ViewObject.hide()
    return strips

def get_similar_edge_direction_in_common_points_from_edges(
        edges : list,
        angle : int = 45,
        ) -> 'pd.DataFram':
    '''
    This function gives a list of edges, finds the common points of those edges.
    Then for each point and each edge of all edges that connected to this point,
    it searches for similar directions with this edge. The df column's output is
    like "point edge 1 2 3 4" 
    angle is maximum angle between two adjacent slabs
    '''

    import pandas as pd
    cols = ['edge', 'is_first', 'is_end', 'x', 'y', 'z']
    all_edges = []
    for e in edges:
        v1, v2 = e.firstVertex(), e.lastVertex()
        all_edges.append([e, True, False, v1.X, v1.Y, v1.Z])
        all_edges.append([e, False, True, v2.X, v2.Y, v2.Z])
    df = pd.DataFrame(all_edges, columns=cols)
    group = df.groupby(['x','y', 'z'])
    max_number_edges_connect_to_point = group['edge'].count().max()
    additional_cols = [n for n in range(1, max_number_edges_connect_to_point)]
    cols=['point', 'edge'] + additional_cols
    df1 = []
    for state, frame in group:
        edges_from_point = list(frame['edge'])
        for edge in edges_from_point:
            edges_without_curr_edge = set(edges_from_point).difference([edge])
            preferable_edges = get_in_direction_priority(edge, edges_without_curr_edge, angle)
            none_exist_edge_len = max_number_edges_connect_to_point -  len(preferable_edges) - 1
            preferable_edges += none_exist_edge_len * [None]
            df1.append([state, edge] +  preferable_edges)
    df1 = pd.DataFrame(df1, columns=cols)
            
    map_dict_edges_to_num = dict()
    for i, e in enumerate(edges, start=1):
        map_dict_edges_to_num[e] = i
    edges_cols = ['edge'] + additional_cols
    for col in (edges_cols):
        df1[col] = df1[col].map(map_dict_edges_to_num)
    df1 = df1.fillna(0)
    for col in (edges_cols):
        df1[col] = df1[col].astype(int)
    return df1

def is_similar_direction(edge1, edge2, angle_threshold=45):
    angle_diff = angle_between_two_edges(edge1, edge2)
    return (angle_diff >= 180 - angle_threshold)

def get_number_of_edges_connect_to_point(p, edges, used=[]):
    """
    Count the number of edges connected to a given point p.

    Parameters:
    p (FreeCAD.Vector): The point to check connections for.
    edges (list): A list of edges, where each edge is a tuple of two FreeCAD.Vector points.

    Returns:
    int: The number of edges connected to the point p.
    """
    count = 0
    for i, edge in enumerate(edges):
        start, end = edge.Vertexes
        if (is_equal_two_points(start, p) or is_equal_two_points(end, p)) and i not in used:
            count += 1
    return count


def get_continuous_edges_1(
        edges : list,
        threshol_angle : int = 45,
        ):
    '''
    This function gets a list of edges and search for groups of edges that create
    continuous edges in x or y direction
    '''
    grouped = []
    used = set()

    for i, edge in enumerate(edges):
        if i in used:
            continue
        current_group = [i]
        used.add(i)

        # Explore connected lines
        stack = [edge]
        while stack and len(used) < len(edges):
            current_edge = stack.pop()
            desired_edge = current_edge
            while desired_edge:
                desired_edge = None
                suitable = False
                max_angle = 180 - threshol_angle
                for j, other_edge in enumerate(edges):
                    if j in used:
                        continue
                    if is_close(current_edge, other_edge):
                        angle = angle_between_two_edges(current_edge, other_edge)
                        if angle >= max_angle:
                            # search in edges that unused and maybe sutiable for get to joint with other_edge
                            # p = get_common_vector_in_two_edges(other_edge, current_edge)
                            # n = get_number_of_edges_connect_to_point(p, edges, used)
                            # if n == 1:
                            #     desired_edge = other_edge
                            #     # max_angle = angle
                            #     index = j
                            #     suitable = True
                            #     break
                            # else:
                            #     suitable = True
                            #     for k, maybe_suitable_edge in enumerate(edges):
                            #         if k in used or k == j:
                            #             continue
                            #         if is_close(other_edge, maybe_suitable_edge):
                            #             maybe_suitable_angle = angle_between_two_edges(other_edge, maybe_suitable_edge)
                            #             if maybe_suitable_angle > angle:
                            #                 suitable = False
                            #                 break
                            # if suitable:
                            desired_edge = other_edge
                            max_angle = angle
                            index = j
                if desired_edge:
                    current_group.append(index)
                    used.add(index)
                    stack.append(desired_edge)

        grouped.append(current_group)
    return grouped

def get_continuous_edges(
        edges : list,
        angle : int = 45,
        ):
    '''
    This function gets a list of edges and search for groups of edges that create
    continuous edges in x or y direction
    '''
    df = get_similar_edge_direction_in_common_points_from_edges(edges, angle)
    all_edges = []
    end = False
    used_edges = []
    continues_edges = []
    edges_cols = list(df.columns)[1:]
    additional_cols = edges_cols[1:]
    for i, row in df.iterrows():
        if end:
            all_edges.append(continues_edges)
            end = False
            df['edge'] = df['edge'].replace([previous_edge], 0)
            if df[edges_cols].sum().sum() == 0:
                break
            continues_edges = []
        while not end:
            if len(continues_edges) == 0:
                filt = (df['edge'] == 0) | (df[edges_cols].sum(axis=1) == 0)
                temp_df = df[~filt]
                if len(temp_df) == 0:
                    end = True
                    break
                j, temp_row = next(temp_df.iterrows())
                edge_num = temp_row['edge']
                point = row['point']
                if not edge_num in used_edges:
                    continues_edges.append(edge_num)
                    used_edges.append(edge_num)
                for col in edges_cols:
                    df.at[j, col] = 0
                df[additional_cols] = df[additional_cols].replace([edge_num], 0)
                
            else:
                previous_edge = continues_edges[-1]
                filt = (df['edge'] == previous_edge) & (df['point'] != point)
                if not True in filt.values:
                    end = True
                    break
                temp_df = df.loc[filt]
                row_num = temp_df.index.to_list()[0]
                end = True
                for col in additional_cols:
                    edge_num = temp_df.at[row_num, col]
                    if edge_num != 0 and not edge_num in used_edges:
                        continues_edges.append(edge_num)
                        used_edges.append(edge_num)
                        end = False
                        point = df.at[row_num, 'point']
                        df[additional_cols] = df[additional_cols].replace([edge_num], 0)
                        df['edge'] = df['edge'].replace([previous_edge], 0)
                        break
    return all_edges

def get_continuous_slabs(
        slabs : list,
        angle : int = 45,
        ) -> list:
    '''
    angle is maximum angle between two adjacent slabs
    '''
    edges = [s.Shape.Edges[0] for s in slabs if s.Shape.Edges]
    edges_numbers = get_continuous_edges(edges, angle)
    continuous_slabs = []
    for numbers in edges_numbers:
        continuous_slabs.append([slabs[i-1] for i in numbers])
    return continuous_slabs

def get_in_direction_priority(edge, edges,
        angle: int = 45):
    '''
    Getting an edge and calculate angle between edge and each member of edges and then
    sort them from large to small. angle is acceptable angle that illustrates edge is 
    in direction of other edges
    '''
    acceptable_anlge = 180 - angle
    if len(edges) == 0:
        return []
    edges_angles = []
    for e in edges:
        angle = angle_between_two_edges(edge, e)
        if angle == 0:
            angle = 180
        if angle < acceptable_anlge:
            continue
        edges_angles.append((e, angle))
    edges_angles.sort(key=lambda x: x[1], reverse=True)
    return [a[0] for a in edges_angles]

def dot(vector_a, vector_b):
    return vector_a[0]*vector_b[0]+vector_a[1]*vector_b[1]

def angle_between_two_edges(
    edge1 : Part.Edge,
    edge2 : Part.Edge,
    ):
    # v1 = edge1.tangentAt(0)
    # dx1, dy1 = v1.x, v1.y
    # v2 = edge2.tangentAt(0)
    # dx2, dy2 = v2.x, v2.y
    # if abs(dx1) == abs(dx2): # if two edges are in the same direction, also if dx = 0
    # 	return 180
    p1, p2 = [v.Point for v in edge1.Vertexes]
    p3, p4 = [v.Point for v in edge2.Vertexes]
    p1, p2, p3, p4 = find_common_point(p1, p2, p3, p4)

    x1, x2, y1, y2 = p1.x, p2.x, p1.y, p2.y
    x3, x4, y3, y4 = p3.x, p4.x, p3.y, p4.y
    vector_a = [(x1 - x2), (y1 - y2)]
    vector_b = [(x3 - x4), (y3 - y4)]
    dot_prod = dot(vector_a, vector_b)
    magnitudes_a = dot(vector_a, vector_a) ** 0.5
    magnitudes_b = dot(vector_b, vector_b) ** 0.5
    cosine = dot_prod / magnitudes_b / magnitudes_a
    if cosine > 1:
        cosine = 1
    if cosine < -1:
        cosine = -1
    angle = math.acos(cosine)
    ang_deg = math.degrees(angle)%360
    if ang_deg-180>=0:
        return 360 - ang_deg
    else: 
        return ang_deg
    
def is_close(edge1, edge2, threshold=0.01):
    return any((
        np.linalg.norm(edge1.firstVertex().Point - edge2.firstVertex().Point) < threshold,
        np.linalg.norm(edge1.firstVertex().Point - edge2.lastVertex().Point) < threshold,
        np.linalg.norm(edge1.lastVertex().Point - edge2.firstVertex().Point) < threshold,
        np.linalg.norm(edge1.lastVertex().Point - edge2.lastVertex().Point) < threshold,
    ))

def find_common_point(p1, p2, p3, p4):
    if is_equal_two_points(p1, p3, .001):
        return p1, p2, p1, p4
    elif is_equal_two_points(p1, p4, .001):
        return p1, p2, p1, p3
    elif is_equal_two_points(p2, p3, .001):
        return p2, p1, p2, p4
    elif is_equal_two_points(p2, p4, .001):
        return p2, p1, p2, p3

def get_coordinate_and_width_between(min_coord, max_coord, width, equal=True) -> dict:
    '''
    divide space between min_coord and max_coord with distanc = width,
    if equal, it calculate new width that divide space equally
    '''
    dist = max_coord - min_coord
    n = int(dist // width)
    # if n == 0:
    #     coord = (max_coord + min_coord) / 2
    #     return {coord : dist}
    if equal:
        width = dist / n
        remain = 0
    else:
        remain = dist % width
    coords_width = dict()
    coord = min_coord
    for i in range(n):
        if i == n - 1:
            coord = coord + width + remain / 2
            coords_width[coord] = width + remain
        else:
            coord = min_coord + (0.5 + i) * width
            coords_width[coord] = width

    return coords_width

def get_coordinate_and_width_betweens(coords: list, width, equal=False):
    coords_width = dict()
    for min_coord, max_coord in zip(coords[: -1], coords[1:]):
        coords_width.update(get_coordinate_and_width_between(min_coord, max_coord, width, equal))
    return coords_width


def get_xy_coords_width_in_mat_foundation(
            foundation = None,
            openings : Union[list, bool] = None,
            x_width : float = 1000,
            y_width : Union[float, bool] = None,
            equal : bool = False,
            consider_openings: bool = True,
            ):
    if foundation is None:
        foundation = FreeCAD.ActiveDocument.Foundation
    if openings is None:
        openings = foundation.openings
    if not consider_openings:
        openings = None
    if y_width is None:
        y_width = x_width
    foundation_bb = foundation.Shape.BoundBox
    x_min_f = foundation_bb.XMin
    y_min_f = foundation_bb.YMin
    x_max_f = foundation_bb.XMax
    y_max_f = foundation_bb.YMax
    if openings:
        opening = openings[0]
        opening_bb = opening.Shape.BoundBox
        x_min_o = opening_bb.XMin
        y_min_o = opening_bb.YMin
        x_max_o = opening_bb.XMax
        y_max_o = opening_bb.YMax
        x_coords = [x_min_f, x_min_o, x_max_o, x_max_f]
        y_coords = [y_min_f, y_min_o, y_max_o, y_max_f]
    else:
        x_coords = [x_min_f, x_max_f]
        y_coords = [y_min_f, y_max_f]

    x_coords_width = get_coordinate_and_width_betweens(
            x_coords,
            y_width,
            equal=equal,
            )
    y_coords_width = get_coordinate_and_width_betweens(
            y_coords,
            x_width,
            equal=equal,
            )
    return x_coords_width, y_coords_width

def draw_strip_automatically_in_mat_foundation(
            foundation = None,
            openings : Union[list, bool] = None,
            x_width : float = 1000,
            y_width : Union[float, bool] = None,
            equal : bool = False,
            x_layer_name = 'A',
            y_layer_name = 'B',
            draw_x : bool = True,
            draw_y : bool = True,
            consider_openings : bool = True,
            ):
    if foundation is None:
        foundation = FreeCAD.ActiveDocument.Foundation
    x_coords_width, y_coords_width = get_xy_coords_width_in_mat_foundation(
            foundation,
            openings,
            x_width,
            y_width,
            equal,
            consider_openings=consider_openings,
    )
    foundation_bb = foundation.Shape.BoundBox
    x_min_f = foundation_bb.XMin
    y_min_f = foundation_bb.YMin
    x_max_f = foundation_bb.XMax
    y_max_f = foundation_bb.YMax
    z = foundation.level.Value
    import BOPTools.SplitAPI as sp
    
    i = j = 0
    if draw_x:
        x_strips = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","x_strips")
        y_lines = []
        for y in y_coords_width.keys():
            p1 = (x_min_f, y, z)
            p2 = (x_max_f, y, z)
            y_lines.append(Part.makeLine(p1, p2))
        y_slices = sp.slice(foundation.plan, y_lines, 'Split')
        for edge in y_slices.Edges:
            bb = edge.BoundBox
            if bb.YLength == 0:
                y = bb.YMin
                width = y_coords_width.get(y, None)
                if width is not None:
                    i += 1
                    points = [v.Point for v in edge.Vertexes]
                    wire = Draft.make_wire(points, face=False)
                    s = strip.make_strip(wire, layer=x_layer_name, width=width)
                    s.Label = f'CS{x_layer_name}{i}'
                    x_strips.addObject(s)
    if draw_y:
        y_strips = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","y_strips")
        x_lines = []
        for x in x_coords_width.keys():
            p1 = (x, y_min_f, z)
            p2 = (x, y_max_f, z)
            x_lines.append(Part.makeLine(p1, p2))
        x_slices = sp.slice(foundation.plan, x_lines, 'Split')
        for edge in x_slices.Edges:
            bb = edge.BoundBox
            if bb.XLength == 0:
                x = bb.XMin
                width = x_coords_width.get(x, None)
                if width is not None:
                    j += 1
                    points = [v.Point for v in edge.Vertexes]
                    wire = Draft.make_wire(points, face=False)
                    s = strip.make_strip(wire, layer=y_layer_name, width=width)
                    s.Label = f'CS{y_layer_name}{j}'
                    y_strips.addObject(s)

def draw_strip_from_base_foundation(
            base_foundation,
            i,
            j,
            split: bool=False,
            tolerance: float=1e-7,
            ):
    '''
    split: If a strip is not straight, break the strip in some parts
    '''
    layer = base_foundation.layer
    edges = []
    if not base_foundation.first_edge.isNull():
        edges.append(base_foundation.first_edge)
    edges.extend(base_foundation.Base.Shape.Edges)
    if not base_foundation.last_edge.isNull():
        edges.append(base_foundation.last_edge)
    points = get_points_from_indirection_edges(edges=edges, tol=tolerance)
    strips = []
    if split and len(points) > 2:
        for p1, p2 in zip(points[0:-1], points[1:]):
            wire = Draft.make_wire([p1, p2], face=False)
            s = strip.make_strip(
                                wire,
                                layer=layer, 
                                width=base_foundation.width.Value,
                                left_width=base_foundation.left_width.Value,
                                right_width=base_foundation.right_width.Value,
                                align = base_foundation.align,
                                )
            if layer == 'A':
                i += 1
                strip_name = f'CS{layer}{i}'
            else:
                j += 1
                strip_name = f'CS{layer}{j}'
            s.Label = strip_name
            strips.append(s)
    else:
        wire = Draft.make_wire(points, face=False)
        s = strip.make_strip(
                        wire,
                        layer=layer, 
                        width=base_foundation.width.Value,
                        left_width=base_foundation.left_width.Value,
                        right_width=base_foundation.right_width.Value,
                        align = base_foundation.align,
                        )
        if layer == 'A':
            i += 1
            strip_name = f'CS{layer}{i}'
            strips.append(s)
        else:
            j += 1
            strip_name = f'CS{layer}{j}'
            strips.append(s)
        s.Label = strip_name
    return strips, i, j

def draw_strip_automatically_in_strip_foundation(
            foundation = None,
            split: bool=False,
            tolerance: float=1e-7,
            base_foundations: Union[list, None] = None,
            # openings : Union[list, bool] = None,
            # y_width : Union[float, bool] = None,
            # equal : bool = False,
            # x_layer_name = 'A',
            # draw_x : bool = True,
            ):
    '''
    split: If a strip is not straight, break the strip in some parts
    '''
    if base_foundations is None:
        if foundation is None:
            foundation = FreeCAD.ActiveDocument.Foundation
        base_foundations = foundation.base_foundations
    a_strips = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","A_strips")
    b_strips = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","B_strips")
    i = j = 0
    for base_foundation in base_foundations:
        strips, i, j = draw_strip_from_base_foundation(
            base_foundation=base_foundation,
            i=i,
            j=j,
            split=split,
            tolerance=tolerance,
            )
        for s in strips:
            if s.layer == 'A':
                a_strips.addObject(s)
            elif s.layer == 'B':
                b_strips.addObject(s)
    return a_strips, b_strips

def is_straight_line(edges, tol=1e-7):
    if len(edges) > 1:
        start_edge = edges[0]
        dir_start_edge = start_edge.tangentAt(start_edge.FirstParameter)
        for edge in edges:
            dir_edge = edge.tangentAt(edge.FirstParameter)
            if dir_start_edge.cross(dir_edge).Length > tol:
                return False
    return True

def get_points_from_indirection_edges(edges, tol=1e-7):
    new_edges = []
    for e in edges:
        try:
            if hasattr(e, "FirstParameter"):
                new_edges.append(e)
        except:
            continue
    edges = new_edges
    points = [edges[0].firstVertex().Point]
    if len(edges) > 1:
        for e1, e2 in zip(edges[0:-1], edges[1:]):
            dir_e1 = e1.tangentAt(e1.FirstParameter)
            dir_e2 = e2.tangentAt(e2.FirstParameter)
            if dir_e1.cross(dir_e2).Length > tol:
                points.append(e1.lastVertex().Point)
    points.append(edges[-1].lastVertex().Point)
    return points

def remove_colinear_edges(
        edges: Union[list, Part.Face],
        tol : float = 0,
        ):
    face = False
    if isinstance(edges, (Part.Face, Part.Wire)):
        edges = Part.__sortEdges__(edges.Edges)
        face = True
    p1 = edges[0].firstVertex().Point
    points = [p1]
    es = []
    if len(edges) > 1:
        for e1, e2 in zip(edges[0:-1], edges[1:]):
            dir_e1 = e1.tangentAt(e1.FirstParameter)
            dir_e2 = e2.tangentAt(e2.FirstParameter)
            curr_len = dir_e1.cross(dir_e2).Length
            # print(f"{curr_len=}\n")
            if curr_len > tol:
                p2 = get_common_vector_in_two_edges(e1, e2, tol=.01)
                # p2 = e1.lastVertex().Point
                es.append(Part.makeLine(p1, p2))
                points.append(p2)
                p1 = p2
    p2 = edges[-1].lastVertex().Point
    points.append(p2)
    es.append(Part.makeLine(p1, p2))
    if face:
        points.append(points[0])
        wire = Part.makePolygon(points)
        es = Part.Face(wire)
    return es

def get_objects_of_type(
        type_: str,
        doc=None,
        ):
    if doc is None:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return []
    objs = []
    for o in doc.Objects:
        if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == type_:
            objs.append(o)
    return objs

def get_objects_of_ifc_type(
        type_: str,
        doc=None,
        ):
    if doc is None:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return []
    objs = []
    for o in doc.Objects:
        if hasattr(o, "IfcType") and o.IfcType == type_:
            objs.append(o)
    return objs

def get_beams(doc=None):
    beams = []
    if doc is None:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return beams
    for o in doc.Objects:
        if (
            hasattr(o, "type") and
            o.type == 'Beam'
            ):
            beams.append(o)
    return beams
        

def is_beam_shape_on_base_foundations_base(
        beam,
        base_foundations : list=None,
        ):
    if base_foundations is None:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return False
        base_foundations = get_objects_of_type('BaseFoundation', doc)
    if len(base_foundations) == 0:
        return False
    p1, p2 = beam.Points
    mid_point = (p1 + p2) / 2
    for bf in base_foundations:
        if bf.Shape.isInside(mid_point, .01, True):
            return True
    return False

def get_beams_in_doc_that_belogns_to_base_foundations(doc= None):
    '''
    Search in doc for beams that their geometry are in Base of base foundations in model
    '''
    ret = set()
    if doc is None:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return ret
    base_foudations = get_objects_of_type('BaseFoundation', doc)
    beams = get_beams(doc)
    for beam in beams:
        if is_beam_shape_on_base_foundations_base(beam=beam, base_foundations=base_foudations):
            ret.add(beam.Name)
    return ret


def get_sorted_points(
            edges,
            vector=True,
            last=False,
            sort_edges=True,
            ):
    points = []
    if sort_edges:
        edges = Part.__sortEdges__(edges)
    for e in edges:
        v = e.firstVertex()
        if vector:
            points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
        else:
            points.append(v)
    if last:
        v = e.lastVertex()
        if vector:
            points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
        else:
            points.append(v)
    return points

def get_total_length_of_shapes(shapes: List[Part.Shape]):

    """ get total length of Shapes."""
    total_len = 0
    for shape in shapes:
        if hasattr(shape, "Length"):
            total_len += shape.Length
    return total_len

def get_total_volume_of_shapes(shapes: List[Part.Shape]):

    """ get total volume of Shapes."""
    total_volume = 0
    for shape in shapes:
        if hasattr(shape, "Volume"):
            total_volume += shape.Volume
    return total_volume

def get_color(param, pref_intity, color=674321151):
    c = param.GetUnsigned(pref_intity, color)
    r = float((c >> 24) & 0xFF) / 255.0
    g = float((c >> 16) & 0xFF) / 255.0
    b = float((c >> 8) & 0xFF) / 255.0
    return (r, g, b)

def get_display_mode(param, pref_intity, number=0):
    n = param.GetInt(pref_intity, number)
    return {
        0: 'Flat Lines',
        1: 'Shaded',
        2: 'Wireframe',
        }[n]

def format_view_object(
    obj,
    shape_color_entity: str,
    line_width_entity: str = 'aaaaa',
    transparency_entity: str = 'aaaaa',
    display_mode_entity: str = 'aaaaa',
    point_size_entity: str = 'aaaaa',
    line_color_entity: Union[bool, str] = None,
    point_color_entity: Union[bool, str] = None,
    ):
    if FreeCAD.GuiUp:
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        shape_color = get_color(
            param=param,
            pref_intity=shape_color_entity,
            )
        display_mode = get_display_mode(
            param=param,
            pref_intity=display_mode_entity,
            )
        line_width = param.GetFloat(line_width_entity, 1.0)
        point_size = param.GetFloat(point_size_entity, 1.0)
        transparency = int(param.GetFloat(transparency_entity, 0))
        if line_color_entity is None:
            line_color = shape_color
        else:
            line_color = get_color(
                param=param,
                pref_intity=line_color_entity,
                )
        if point_color_entity is None:
            point_color = line_color
        else:
            point_color = get_color(
                param=param,
                pref_intity=point_color_entity,
                )

        obj.ViewObject.LineWidth = line_width
        obj.ViewObject.PointSize = point_size
        obj.ViewObject.DisplayMode = display_mode
        obj.ViewObject.ShapeColor = shape_color
        obj.ViewObject.LineColor = line_color
        obj.ViewObject.PointColor = point_color
        obj.ViewObject.Transparency = transparency