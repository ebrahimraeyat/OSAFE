from typing import List, Union
import math

import FreeCAD
import Part

from etabs_api.frame_obj import FrameObj


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
	cut = sh1.cut(sh2)
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
	foun_plan = punch.foundation.plane.copy()
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
			if (p1.isEqual(p3, .1) and p2.isEqual(p4, .1)) or \
				(p1.isEqual(p4, .1) and p2.isEqual(p3, .1)):
				null_edges.append('No')
				break
		else:
			null_edges.append('Yes')
	return null_edges, common_edges

def punch_null_points(
	punch,
	) -> tuple:
	null_edges, common_edges = punch_null_edges(punch)
	null_points_in_general = get_sort_points(common_edges)
	null_points_in_local = []
	for point in null_points_in_general:
		null_points_in_local.append(point.sub(punch.center_of_punch))
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

def lenght_of_edges(
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
	gives faces and return the center of mass coordinate
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

def moment_inersia(
	faces: List[Part.Face],
	):
	'''
	return rotational moment inersia of faces list Ixx, Iyy
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
	from functools import reduce
	import operator
	center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
	return sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)

def get_sort_points(
	edges,
	vector=True,
	get_last=False,
	):
	vectors = []
	if len(edges) == 1:
		for v in edges[0].Vertexes:
			vectors.append(FreeCAD.Vector(v.X, v.Y, v.Z))
		return vectors
	edges = Part.__sortEdges__(edges)
	for e1, e2 in zip(edges[:-1], edges[1:]):
		p = get_common_vector_in_two_edges(e1, e2)
		vectors.append(p)
	# add first point
	e = edges[0]
	v1 = e.firstVertex()
	p1 = FreeCAD.Vector(v1.X, v1.Y, v1.Z)
	p = vectors[0]
	if p1.isEqual(p, True):
		v1 = e.lastVertex()
		p1 = FreeCAD.Vector(v1.X, v1.Y, v1.Z)
	vectors.insert(0, p1)
	if get_last:
		last_edges = edges[-1]
		v2 = last_edges.lastVertex()
		p2 = FreeCAD.Vector(v2.X, v2.Y, v2.Z)
		p = vectors[-1]
		if p.isEqual(p2, True):
			v2 = e.firsVertex()
			p2 = FreeCAD.Vector(v2.X, v2.Y, v2.Z)
		vectors.append(p2)

	if vector:
		return vectors
	else:
		return [Part.Vertex(v) for v in vectors]

def get_common_vector_in_two_edges(e1, e2) -> FreeCAD.Vector:
	v1 = e1.firstVertex()
	v2 = e1.lastVertex()
	v3 = e2.firstVertex()
	v4 = e2.lastVertex()
	p1 = FreeCAD.Vector(v1.X, v1.Y, v1.Z)
	p2 = FreeCAD.Vector(v2.X, v2.Y, v2.Z)
	p3 = FreeCAD.Vector(v3.X, v3.Y, v3.Z)
	p4 = FreeCAD.Vector(v4.X, v4.Y, v4.Z)
	if p2.isEqual(p3, True) or p2.isEqual(p4, True):
		return p2
	else:
		return p1

def get_obj_points_with_scales(
	shape : Part.Shape, 
	scales : list = [.75, .5],
	) -> list:
	vertexes = get_sort_points(shape.Edges)
	center_of_mass = shape.CenterOfMass
	lines = []
	for v in vertexes:
		line = Part.makeLine(v, center_of_mass)
		lines.append(line)
	original_points = [FreeCAD.Vector(vec.x, vec.y, vec.z) for vec in vertexes]
	scale_points = []
	scale_points.append(original_points)
	for scale in scales:
		points = []
		for line in lines:
			point = line.valueAt((1 - scale) * line.Length)
			points.append(point)
		scale_points.append(points)
	return scale_points

def get_scale_area_points_with_scale(
	shape : Part.Shape, 
	scales : list = [.75, .5],
	) -> list:
	scale_points = get_obj_points_with_scales(shape, scales)
	area_points = []
	for points1, points2  in zip(scale_points[:-1], scale_points[1:]):
		n = len(points1) // 2
		points11 = points1[:n + 1]
		points12 = points1[n:]
		points21 = points2[:n + 1]
		points22 = points2[n:]
		points21.reverse()
		points22.reverse()
		area_points.extend((
			points11 + points21,
			points12 + points22,
			))
	area_points.append(scale_points[-1])
	return area_points

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
	area1 = face.cut(s1)
	area2 = s1.cut(s2)
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

def get_points_connections_from_slabs(slabs):
	d = {}
	for s in slabs:
		v1 = s.start_point
		v2 = s.end_point
		for v in (v1, v2):
			p = (v.x, v.y, v.z)
			current_slabs = d.get(p, None)
			if current_slabs is None:
				d[p] = [s]
			else:
				d[p].append(s)
	return d

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
	length : float = 2000,
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
		if new_d > d:
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
		x1, y1, x2, y2 = FrameObj.offset_frame_points(x1, y1, x2, y2, distance, neg)
		new_start_point = FreeCAD.Vector(x1, y1, p1.z)
		new_end_point = FreeCAD.Vector(x2, y2, p2.z)
		return new_start_point, new_end_point

def get_common_part_of_slabs(slabs):
	if len(slabs) < 2:
		return None
	shapes = []
	for s in slabs:
		p1, p2 = extend_two_points(s.start_point, s.end_point)
		p1, p2 = get_offset_points(p1, p2, s.offset)
		points = get_width_points(p1, p2, s.width.Value/2, s.angle)
		points.append(points[0])
		shapes.append(Part.Face(Part.makePolygon(points)))
	comm = shapes[0]
	for sh in shapes[1:]:
		comm = comm.common(sh)
	return comm

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

def make_strips_from_slabs(
		slabs : list,
		angle : int = 45,
		):
	'''
	angle is for finding continuous strip, with max angle between two adjacent slabs
	'''
	from safe.punch.strip import make_strip
	continuous_points, _ = get_continuous_points_from_slabs(slabs, angle)
	strips = []
	for points in continuous_points:
		p1, p2 = points[:2]
		dx = abs(p1.x - p2.x)
		dy = abs(p1.y - p2.y)
		if dx > dy:
			layer = 'A'
		else:
			layer = 'B'
		strip = make_strip(points, layer, 'column')
		strips.append(strip)
	return strips

def make_automatic_stirps_in_strip_foundation(
		slabs,
		width,
		north_dist : Union[float, bool] = None,
		south_dist : Union[float, bool] = None,
		east_dist : Union[float, bool] = None,
		west_dist : Union[float, bool] = None,
		x_stirp_name : str = 'A',
		y_stirp_name : str = 'B',
		angle : int = 45,
		):
	from safe.punch.strip import make_strip
	continuous_points, continuous_beams = get_continuous_points_from_slabs(slabs, angle)
	strips = []
	for i, points in enumerate(continuous_points):
		p1, p2 = points[:2]
		dx = abs(p1.x - p2.x)
		dy = abs(p1.y - p2.y)
		if dx > dy:
			layer = x_stirp_name
		else:
			layer = y_stirp_name
		strip = make_strip(points, layer, 'column', None, width)
		strip.beams = continuous_beams[i]
		strips.append(strip)
	return strips

def get_common_parts_of_foundation_slabs(foundation):
	points_slabs = get_points_connections_from_slabs(foundation.tape_slabs)
	points_common_part = {}
	for p, slabs in points_slabs.items():
		comm = get_common_part_of_slabs(slabs)
		if comm is None:
			continue
		points_common_part[p] = comm
	return points_common_part

def get_foundation_plane_without_openings(
	foundation,
	) -> Part.Face:
	slabs = foundation.tape_slabs
	points_common_part = get_common_parts_of_foundation_slabs(foundation)
	common_parts = list(points_common_part.values())
	solids = [f.extrude(FreeCAD.Vector(0, 0, -1)) for f in [s.plane for s in slabs] + common_parts]
	shape = solids[0].fuse(solids[1:])
	shape = shape.removeSplitter()
	for f in shape.Faces:
		if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == foundation.level.Value:
			foundation_plane = f
			break
	if foundation.foundation_type == 'Strip':
		plan = foundation_plane
	elif foundation.foundation_type == 'Mat':
		plan = Part.Face(foundation_plane.OuterWire)
	return plan

def get_foundation_plan_with_openings(
	foundation,
	) -> Part.Face:
	plan_without_openings = get_foundation_plane_without_openings(foundation)
	plan_with_openings = plan_without_openings.copy()
	if len(foundation.openings) > 0:
		new_shape = plan_with_openings.extrude(FreeCAD.Vector(0, 0, -1))
		new_shape = new_shape.cut([o.Shape for o in foundation.openings])
		for f in new_shape.Faces:
			if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == foundation.level.Value:
				plan_with_openings = f
				break
	return plan_with_openings, plan_without_openings

def get_foundation_plan_with_holes(
	foundation,
	) -> Part.Face:
	plan_with_openings, plan_without_openings = get_foundation_plan_with_openings(foundation)
	if foundation.foundation_type == 'Strip':
		mat = Part.Face(plan_with_openings.OuterWire)
		cut = mat.cut([plan_with_openings])
		holes = cut.SubShapes
	elif foundation.foundation_type == 'Mat':
		holes = [o.plane for o in foundation.openings]
	return plan_with_openings, plan_without_openings, holes

def get_points_of_foundation_plan_and_holes(
	foundation,
	) -> list:
	plan_with_openings, plan_without_openings, holes = get_foundation_plan_with_holes(foundation)
	points = []
	if foundation.foundation_type == 'Strip':
		edges_list = [plan.Edges for plan in [plan_with_openings] + holes]
	elif foundation.foundation_type == 'Mat':
		edges_list = [plan.Edges for plan in [plan_without_openings] + holes]
	for edges in edges_list:
		points.append(get_sort_points(edges))
	return points

def get_similar_edge_direction_in_common_points_from_edges(
		edges : list,
		angle : int = 45,
		) -> 'pd.DataFram':
	'''
	This function give a list of edges, find the common points of those edges.
	then for each point and each edge of all edges that connected to this point,
	it search for similarity direction with this edge. the df columns output is
	like "point edge 1 2 3 4" 
	angle is maximum angle between two adjacent slabs
	'''

	import pandas as pd
	cols = ['edge', 'is_first', 'is_end', 'x', 'y', 'z']
	df = pd.DataFrame()
	for e in edges:
		v1, v2 = e.firstVertex(), e.lastVertex()
		se = pd.Series([e, True, False, v1.X, v1.Y, v1.Z], index=cols)
		df = df.append(se, ignore_index=True)
		se = pd.Series([e, False, True, v2.X, v2.Y, v2.Z], index=cols)
		df = df.append(se, ignore_index=True)
	group = df.groupby(['x','y', 'z'])
	max_number_edges_connect_to_point = group['edge'].count().max()
	additional_cols = [n for n in range(1, max_number_edges_connect_to_point)]
	df1 = pd.DataFrame(columns=['point', 'edge'] + additional_cols)
	for state, frame in group:
		edges_from_point = list(frame['edge'])
		for edge in edges_from_point:
			edges_without_curr_edge = set(edges_from_point).difference([edge])
			preferable_edges = get_in_direction_priority(edge, edges_without_curr_edge, angle)
			none_exist_edge_len = max_number_edges_connect_to_point -  len(preferable_edges) - 1
			preferable_edges += none_exist_edge_len * [None]
			se = pd.Series([state, edge] +  preferable_edges, index=df1.columns)
			df1 = df1.append(se, ignore_index=True)
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

def get_continuous_edges(
		edges : list,
		angle : int = 45,
		):
	'''
	This function get a list of egdes and search for groups of egdes that create continuous edges in x or y direction
	angle is maximum angle between two adjacent slabs
	
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
	edges = [s.Shape.Edges[0] for s in slabs]
	edges_numbers = get_continuous_edges(edges, angle)
	continuous_slabs = []
	for numbers in edges_numbers:
		continuous_slabs.append([slabs[i-1] for i in numbers])
	return continuous_slabs

def get_continuous_points_from_slabs(
		slabs : list,
		angle : int = 45,
		) -> list:
	'''
	This function get a list of slabs and calculate continuous slabs.
	then it return a list contain list of continuous points in each 
	list of slabs

	angle is maximum angle between two adjacent slabs
	'''
	continuous_slabs = get_continuous_slabs(slabs, angle)
	continuous_points = []
	for ss in continuous_slabs:
		edges = [s.Shape.Edges[0] for s in ss]
		points = get_sort_points(edges, get_last=True)
		continuous_points.append(points)
	return continuous_points, continuous_slabs
	

def get_in_direction_priority(edge, edges,
		angle: int = 45):
	'''
	Getting an edge and calculate angle between edge and each member of edges and then
	sort them from large to small. angle is acceptable angle that ilustrate edge is in direction
	of other edges
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
	angle = math.acos(dot_prod / magnitudes_b / magnitudes_a)
	ang_deg = math.degrees(angle)%360
	if ang_deg-180>=0:
		return 360 - ang_deg
	else: 
		return ang_deg

def find_common_point(p1, p2, p3, p4):
	if p1.isEqual(p3, .001):
		return p1, p2, p1, p4
	elif p1.isEqual(p4, .001):
		return p1, p2, p1, p3
	elif p2.isEqual(p3, .001):
		return p2, p1, p2, p4
	elif p2.isEqual(p4, .001):
		return p2, p1, p2, p3


	

	





	


	
