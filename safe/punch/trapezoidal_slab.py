import math
import Part
import FreeCAD


def make_trapezoidal_slab(p1, p2, swl, swr, ewl, ewr, height=1000, layer='A', design_type='column'):
	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "TrapezoidalSlab")
	TrapezoidalSlab(obj)
	obj.start_point = p1
	obj.end_point = p2
	obj.layer = layer
	obj.design_type = design_type
	obj.start_width_left = swl
	obj.start_width_right = swr
	obj.end_width_left = ewl
	obj.end_width_right = ewr
	obj.height = height
	if FreeCAD.GuiUp:
		_ViewProviderStrip(obj.ViewObject)
	FreeCAD.ActiveDocument.recompute()
	return obj


class TrapezoidalSlab:
	def __init__(self, obj):
		obj.Proxy = self
		self.Type = 'trapezoidal_slab'
		self.set_properties(obj)

	def set_properties(self, obj):
		if not hasattr(obj, "start_point"):
			obj.addProperty(
				"App::PropertyVector",
				"start_point",
				"Geometry",
				)
		if not hasattr(obj, "end_point"):
			obj.addProperty(
				"App::PropertyVector",
				"end_point",
				"Geometry",
				)
		if not hasattr(obj, "layer"):
			obj.addProperty(
				"App::PropertyString",
				"layer",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "design_type"):
			obj.addProperty(
				"App::PropertyString",
				"design_type",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "start_width_left"):
			obj.addProperty(
				"App::PropertyLength",
				"start_width_left",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "start_width_right"):
			obj.addProperty(
				"App::PropertyLength",
				"start_width_right",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "end_width_left"):
			obj.addProperty(
				"App::PropertyLength",
				"end_width_left",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "end_width_right"):
			obj.addProperty(
				"App::PropertyLength",
				"end_width_right",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "height"):
			obj.addProperty(
			"App::PropertyLength",
			"height",
			"slab",
			)
		if not hasattr(obj, "angle"):
			obj.addProperty(
				"App::PropertyAngle",
				"angle",
				"Geometry", "")
		if not hasattr(obj, "plane"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"plane",
				"TrapezoidalSlab",
				)
		if not hasattr(obj, "solid"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"solid",
				"TrapezoidalSlab",
				)

	def onChanged(self, obj, prop):
		return

	def execute(self, obj):
		p1 = obj.start_point
		p2 = obj.end_point
		obj.Shape = Part.makeLine(p1, p2)
		v = obj.end_point - obj.start_point
		obj.angle = math.atan2(v.y, v.x)
		self.create_width(obj)

	def create_width(self, obj):
		points = []
		xs = obj.start_point.x
		ys = obj.start_point.y
		xe = obj.end_point.x
		ye = obj.end_point.y
		sl = obj.start_width_left.Value
		sr = obj.start_width_right.Value
		el = obj.end_width_left.Value
		er = obj.end_width_right.Value
		teta = obj.angle
		_sin = math.sin(teta)
		_cos = math.cos(teta)
		x = xs - sl * _sin
		y = ys + sl * _cos
		points.append(FreeCAD.Vector(x, y, 0))
		x = xs + sr * _sin
		y = ys - sr * _cos
		points.append(FreeCAD.Vector(x, y, 0))
		x = xe + er * _sin
		y = ye - er * _cos
		points.append(FreeCAD.Vector(x, y, 0))
		x = xe - el * _sin
		y = ye + el * _cos
		points.append(FreeCAD.Vector(x, y, 0))
		points.append(points[0])
		obj.plane = Part.Face(Part.makePolygon(points))
		obj.solid = obj.plane.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))


class _ViewProviderStrip:
	def __init__(self, obj):
		obj.Proxy = self
		obj.addProperty("App::PropertyBool", "show_width", "display", "")

	def attach(self, obj):
		''' Setup the scene sub-graph of the view provider, this method is mandatory '''
		return

	def updateData(self, fp, prop):
		''' If a property of the handled feature has changed we have the chance to handle this here '''
		return

	def execute(self, obj):
		print("view execute!")

	def getDisplayModes(self, obj):
		''' Return a list of display modes. '''
		modes = []
		return modes

	def getDefaultDisplayMode(self):
		''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
		return "Flat Line"

	def setDisplayMode(self, mode):
		''' Map the display mode defined in attach with those defined in getDisplayModes.
		Since they have the same names nothing needs to be done. This method is optional.
		'''
		return mode

	def onChanged(self, vp, prop):
		''' Print the name of the property that has changed '''
		# FreeCAD.Console.PrintMessage("Change View property: " + str(prop) + "\n")
		return

	def getIcon(self):
		''' Return the icon in XMP format which will appear in the tree view. This method is optional
		and if not defined a default icon is shown.
		'''
		return None

	def __getstate__(self):
		''' When saving the document this object gets stored using Python's cPickle module.
		Since we have some un-pickable here -- the Coin stuff -- we must define this method
		to return a tuple of all pickable objects or None.
		'''
		return None

	def __setstate__(self, state):
		''' When restoring the pickled object from document we have the chance to set some
		internals here. Since no data were pickled nothing needs to be done here.
		'''
		return None


if __name__ == "__main__":
	make_trapezoidal_slab(p1=FreeCAD.Vector(0, 16400, 0),
			   p2=FreeCAD.Vector(12210, 16400, 0),
			   swl='25 cm',
			   swr=250,
			   ewl=250,
			   ewr=250,
			   layer='A',
			   design_type='column',
			   )
