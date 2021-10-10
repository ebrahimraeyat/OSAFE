from os.path import join, dirname, abspath
from typing import Union

import FreeCAD
import FreeCADGui
import Part

try:
	from safe.punch import punch_funcs
except:
	import punch_funcs


class Foundation:
	def __init__(self, obj):
		obj.Proxy = self
		self.Type = "Foundation"
		self.set_properties(obj)

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

		if not hasattr(obj, "tape_slabs"):
			obj.addProperty(
				"App::PropertyLinkList",
				"tape_slabs",
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

	def execute(self, obj):
		doc = obj.Document
		tape_slabs = []
		for o in doc.Objects:
			if all(
				[hasattr(o, "Proxy"),
				hasattr(o.Proxy, "Type"),
				o.Proxy.Type in ("tape_slab", "trapezoidal_slab"),
				]):
				tape_slabs.append(o)
		obj.tape_slabs = tape_slabs
		plan = punch_funcs.get_foundation_plane_without_openings(obj)
		obj.plane_without_openings = plan
		new_shape = plan.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
		if len(obj.openings) > 0:
			new_shape = new_shape.cut([o.Shape for o in obj.openings])
		obj.Shape = new_shape
		for f in new_shape.Faces:
			if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
				obj.plane = f
				break
		obj.d = obj.height - obj.cover

	def onDocumentRestored(self, obj):
		obj.Proxy = self
		self.set_properties(obj)
        
class ViewProviderFoundation:

	def __init__(self, vobj):

		vobj.Proxy = self
		vobj.Transparency = 40
		vobj.ShapeColor = (0.32,0.42,1.00)
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
		children=[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.tape_slabs] + \
				[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.openings]
		return children

def make_foundation(
	cover: float = 75,
	fc: int = 25,
	height : int = 800,
	foundation_type : str = 'Strip',
	):
	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
	# obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "Fusion")
	Foundation(obj)
	if FreeCAD.GuiUp:
		ViewProviderFoundation(obj.ViewObject)
	obj.cover = cover
	obj.fc = f"{fc} MPa"
	obj.height = height
	obj.d = height - cover
	obj.foundation_type = foundation_type
	FreeCAD.ActiveDocument.recompute()
	return obj




		