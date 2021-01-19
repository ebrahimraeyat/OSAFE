from typing import List, Union

import FreeCAD
import Part


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

	dx = bx / 2
	dy = by / 2
	v1 = center.add(FreeCAD.Vector(-dx, -dy, 0))
	v2 = center.add(FreeCAD.Vector(dx, -dy, 0))
	v3 = center.add(FreeCAD.Vector(dx, dy, 0))
	v4 = center.add(FreeCAD.Vector(-dx, dy, 0))
	return Part.Face(Part.makePolygon([v1, v2, v3, v4, v1]))


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
	return rotational moment inersia of shell Ixx, Iyy
	'''
	Ixx = 0
	Iyy = 0
	Ixy = 0
	if not center_of_mass(faces):
		return 0, 0, 0
	x_bar, y_bar, z_bar = center_of_mass(faces)
	for f in faces:
		# if f.ViewObject.Visibility == False:
		#	 continue
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
