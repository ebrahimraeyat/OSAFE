from typing import Union

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
	sh1: Part.Shape,
	sh2: Part.Shape,
	d: Union[float, int],
	):
	edges = punch_area_edges(sh1, sh2)
	faces = []
	for e in edges:
		face = e.extrude(FreeCAD.Vector(0, 0, -d))
		faces.append(face)
	return faces
