from os.path import join, dirname, abspath
from typing import Union

import FreeCAD
import FreeCADGui
import Part


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
		new_shape = tape_slabs[0].solid
		for i in tape_slabs[1:]:
			new_shape = new_shape.fuse(i.solid)
		obj.Shape = new_shape.removeSplitter()
		for f in obj.Shape.Faces:
			if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
				foundation_plane = f
				break
		obj.plane = foundation_plane
		obj.d = obj.height - obj.cover
        # if bool(slab_opening):
        #     print('openings')
        #     base = fusion
        #     for opening in slab_opening:
        #         cut = doc.addObject("Part::Cut", "Cut")
        #         cut.Base = base
        #         cut.Tool = opening
        #         base = cut
        #     return cut
        # return fusion

	def onDocumentRestored(self, obj):
		obj.Proxy = self
		self.set_properties(obj)
        
class ViewProviderFoundation:

	def __init__(self, vobj):

		vobj.Proxy = self
		vobj.Transparency = 40
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
		children=[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.tape_slabs]
		return children

def make_foundation(
	cover: float = 75,
	fc: int = 25,
	height : int = 800,
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
	FreeCAD.ActiveDocument.recompute()
	return obj




		