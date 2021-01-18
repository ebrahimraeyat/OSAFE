from os.path import join, dirname, abspath
from typing import Union

import FreeCAD
import FreeCADGui
import Part


class Foundation:
	def __init__(self, obj):
		obj.Proxy = self
		self.set_properties(obj)

	def set_properties(self, obj):

		if not hasattr(obj, "fc"):
			obj.addProperty(
				"App::PropertyPressure",
				"fc",
				"Concrete",
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

		if not hasattr(obj, "shape"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"shape",
				"Foundation",
				)


	def onDocumentRestored(self, obj):
		obj.Proxy = self
		self.set_properties(obj)

	def execute(self, obj):
		d = (obj.height - obj.cover).Value
		sh = obj.shape.extrude(FreeCAD.Vector(0, 0, -d))
		obj.Shape = sh


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



def make_foundation(
	base: Part.Shape = None,
	height: Union[float, str] = 1000,
	cover: Union[float, str] = 75,
	fc: Union[float, str] = 25
	):
	if not base:
		base = FreeCADGui.Selection.getSelection()[0].Shape

	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
	Foundation(obj)
	ViewProviderFoundation(obj.ViewObject)
	obj.shape = base
	obj.height = height
	obj.cover = cover
	obj.fc = f"{fc} MPa"

	FreeCAD.ActiveDocument.recompute()

	return obj




		