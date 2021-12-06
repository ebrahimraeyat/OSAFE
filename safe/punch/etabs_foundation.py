from os.path import join, dirname, abspath
from typing import Union

from PySide2 import QtCore
import FreeCAD
import FreeCADGui
import Part
from safe.punch.base_foundation import BaseFoundation

try:
	from safe.punch import punch_funcs
except:
	import punch_funcs


class Foundation:
	def __init__(self, obj):
		obj.Proxy = self
		self.Type = "Foundation"
		self.set_properties(obj)
		self.obj_name = obj.Name

	def set_properties(self, obj):

		if not hasattr(obj, "fc"):
			obj.addProperty(
				"App::PropertyPressure",
				"fc",
				"Foundation",
				)

		if not hasattr(obj, "height"):
			obj.addProperty(
				"App::PropertyLength",
				"height",
				"Foundation",
				)

		if not hasattr(obj, "cover"):
			obj.addProperty(
				"App::PropertyLength",
				"cover",
				"Foundation",
				)
		if not hasattr(obj, "d"):
			obj.addProperty(
				"App::PropertyLength",
				"d",
				"Foundation",
				)

		if not hasattr(obj, "base_foundations"):
			obj.addProperty(
				"App::PropertyLinkList",
				"base_foundations",
				"Foundation",
				)

		if not hasattr(obj, "plane"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"plane",
				"Foundation",
				)
		if not hasattr(obj, "plane_without_openings"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"plane_without_openings",
				"Foundation",
				)
		if not hasattr(obj, "openings"):
			obj.addProperty(
				"App::PropertyLinkList",
				"openings",
				"Foundation",
				)
		# if not hasattr(obj, "split"):
		# 	obj.addProperty(
		# 		"App::PropertyBool",
		# 		"split",
		# 		"Foundation",
		# 		).split = True
		if not hasattr(obj, "foundation_type"):
			obj.addProperty(
				"App::PropertyEnumeration",
				"foundation_type",
				"Foundation",
				).foundation_type = ['Strip', 'Mat']
		if not hasattr(obj, "continuous_layer"):
			obj.addProperty(
				"App::PropertyEnumeration",
				"continuous_layer",
				"Foundation",
				).continuous_layer = ['A', 'B']
		# if not hasattr(obj, "top_face"):
		# 	obj.addProperty(
		# 		"App::PropertyString",
		# 		"top_face",
		# 		"Foundation",
		# 		)
		# if not hasattr(obj, "loadcases"):
		# 	obj.addProperty(
		# 		"App::PropertyStringList",
		# 		"loadcases",
		# 		"Loads",
		# 		)
		if not hasattr(obj, "level"):
			obj.addProperty(
				"App::PropertyDistance",
				"level",
				"Foundation",
			)
		# if not hasattr(obj, "F2K"):
		# 	obj.addProperty(
		# 		"App::PropertyFile",
		# 		"F2K",
		# 		"Safe",
		# 	)
		if not hasattr(obj, "redraw"):
			obj.addProperty(
				"App::PropertyBool",
				"redraw",
				"Foundation",
				).redraw = False
		obj.setEditorMode('redraw', 2)
		obj.setEditorMode('level', 2)
		obj.setEditorMode('d', 1)
		
	# def onChanged(self, obj, prop):
	# 	if prop == 'F2K':
	# 		obj.redraw = False
	

	def execute(self, obj):
		if obj.redraw:
			obj.redraw = False
			return
		QtCore.QTimer().singleShot(50, self._execute)

	def _execute(self):
		obj = FreeCAD.ActiveDocument.getObject(self.obj_name)
		if not obj:
			FreeCAD.ActiveDocument.recompute()
			return
		obj.redraw = True
		obj.Shape = punch_funcs.get_foundation_shape_from_base_foundations(
				obj.base_foundations,
				height = obj.height.Value,
				foundation_type = obj.foundation_type,
				continuous_layer = obj.continuous_layer,
				openings=obj.openings,
				)
		# obj.plane, obj.plane_without_openings, holes = punch_funcs.get_foundation_plan_with_holes(obj)
		# obj.Shape = obj.plane.copy().extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
		# for i, face in enumerate(obj.Shape.Faces, start=1):
		# 	if face.BoundBox.ZLength == 0 and face.BoundBox.ZMax == obj.level.Value:
		# 		obj.top_face = f'Face{i}'
		# for o in doc.Objects:
		# 	if (
		# 		hasattr(o, 'TypeId') and
		# 		o.TypeId == 'Fem::ConstraintForce'
		# 		):
		# 		o.References = [obj, obj.top_face]
		# obj.d = obj.height - obj.cover
		FreeCAD.ActiveDocument.recompute()

	def onDocumentRestored(self, obj):
		obj.Proxy = self
		self.set_properties(obj)
		obj.redraw = True
		
class ViewProviderFoundation:

	def __init__(self, vobj):

		vobj.Proxy = self
		# vobj.Transparency = 40
		vobj.ShapeColor = (0.45, 0.45, 0.45)
		vobj.DisplayMode = "Shaded"

	def attach(self, vobj):
		self.ViewObject = vobj
		self.Object = vobj.Object

	def getIcon(self):
		return join(dirname(abspath(__file__)), "Resources", "icons","foundation.png")

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

	def claimChildren(self):
		children=[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.base_foundations] + \
				[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.openings]
		return children

def make_foundation(
	cover: float = 75,
	fc: int = 25,
	height : int = 800,
	foundation_type : str = 'Strip',
	# load_cases : list = [],
	base_foundations : Union[list, None] = None,
	continuous_layer : str = 'A',
	):
	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
	Foundation(obj)
	if FreeCAD.GuiUp:
		ViewProviderFoundation(obj.ViewObject)
	obj.cover = cover
	obj.fc = f"{fc} MPa"
	obj.height = height
	obj.d = height - cover
	obj.foundation_type = foundation_type
	if base_foundations is None:
		base_foundations = []
		for o in FreeCAD.ActiveDocument.Objects:
			if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
				base_foundations.append(o)
	level = base_foundations[0].beams[0].start_point.z
	obj.level = level
	obj.base_foundations = base_foundations
	obj.continuous_layer = continuous_layer
	FreeCAD.ActiveDocument.recompute()
	return obj




		