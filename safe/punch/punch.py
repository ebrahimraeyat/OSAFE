import math
from typing import Union
import Part
import FreeCAD
import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP

from safe.punch import punch_funcs


class _Punch:
	def __init__(self, obj):
		obj.Proxy = self
		self.set_properties(obj)
		obj.Location = ['Corner1', 'Corner2', 'Corner3', 'Corner4', 'Edge1', 'Edge2', 'Edge3', 'Edge4', 'Interier']

	def set_properties(self, obj):
		self._location = {
			'Corner3': [(0, -1, 0), (-1, 0, 0)],
			'Corner4': [(0, -1, 0), (1, 0, 0)],
			'Corner1': [(0, 1, 0), (1, 0, 0)],
			'Corner2': [(0, 1, 0), (-1, 0, 0)],
			'Edge3': [(0, -1, 0), (-1, 0, 0), (1, 0, 0)],
			'Edge4': [(0, -1, 0), (1, 0, 0), (0, 1, 0)],
			'Edge1': [(0, 1, 0), (1, 0, 0), (-1, 0, 0)],
			'Edge2': [(0, 1, 0), (-1, 0, 0), (0, -1, 0)],
			'Interier': [(0, 1, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0)]
		}
		if not hasattr(obj, "text"):
			obj.addProperty("App::PropertyLink", "text", "Punch")
		if not hasattr(obj, "faces"):
			obj.addProperty("Part::PropertyPartShape", "faces", "Punch", "", 1, False)
		if not hasattr(obj, "d"):
			obj.addProperty("App::PropertyFloat", "d", "Punch", "", 1, True)
		if not hasattr(obj, "normals"):
			obj.addProperty("App::PropertyVectorList", "normals", "Punch", "", 1, False)
		if not hasattr(obj, "Area"):
			obj.addProperty("App::PropertyFloat", "Area", "Punch")
		if not hasattr(obj, "fc"):
			obj.addProperty("App::PropertyPressure", "fc", "Punch", "", 1, True)
		if not hasattr(obj, "bx"):
			obj.addProperty("App::PropertyFloat", "bx", "Column")
		if not hasattr(obj, "by"):
			obj.addProperty("App::PropertyFloat", "by", "Column")
		if not hasattr(obj, "number"):
			obj.addProperty("App::PropertyInteger", "number", "Column", "", 1, True)
		if not hasattr(obj, "I22"):
			obj.addProperty("App::PropertyFloat", "I22", "Punch", "", 1, True)
		if not hasattr(obj, "I33"):
			obj.addProperty("App::PropertyFloat", "I33", "Punch", "", 1, True)
		if not hasattr(obj, "I23"):
			obj.addProperty("App::PropertyFloat", "I23", "Punch", "", 1, True)
		if not hasattr(obj, "center_of_punch"):
			obj.addProperty("App::PropertyVector",
				"center_of_punch",
				"Punch",
				)
		if not hasattr(obj, "Ratio"):
			obj.addProperty("App::PropertyString", "Ratio", "Punch", "", 1, True).Ratio = '0.'
		if not hasattr(obj, "Location"):
			obj.addProperty("App::PropertyEnumeration", "Location", "Punch")
		if not hasattr(obj, "b0"):
			obj.addProperty("App::PropertyFloat", "b0", "Punch", "", 1, True)
		if not hasattr(obj, "alpha_s"):
			obj.addProperty("App::PropertyInteger", "alpha_s", "Allowable_Stress", "", 1, True)
		if not hasattr(obj, "one_way_shear_capacity"):
			obj.addProperty("App::PropertyForce", "one_way_shear_capacity", "Allowable_Stress", "", 1, True)
		if not hasattr(obj, "Vc"):
			obj.addProperty("App::PropertyForce", "Vc", "Allowable_Stress", "", 1, True)
		if not hasattr(obj, "vc"):
			obj.addProperty("App::PropertyPressure", "vc", "Allowable_Stress", "", 1, True).vc = 1.
		if not hasattr(obj, "Vu"):
			obj.addProperty("App::PropertyPressure", "Vu", "Allowable_Stress", "", 1, True).Vu = 0
		if not hasattr(obj, "combos_load"):
			obj.addProperty(
				"App::PropertyMap",
				"combos_load",
				"Column",
				)

		if not hasattr(obj, "combos_ratio"):
			obj.addProperty(
				"App::PropertyMap",
				"combos_ratio",
				"Result",
				)

		if not hasattr(obj, "foundation_plane"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"foundation_plane",
				"Punch",
				)

		if not hasattr(obj, "fondation"):
			obj.addProperty(
				"App::PropertyLink",
				"foundation",
				"Foundation",
				)

		if not hasattr(obj, "center_of_load"):
			obj.addProperty(
				"App::PropertyVector",
				"center_of_load",
				"Column",
				)

		if not hasattr(obj, "user_location"):
			obj.addProperty(
			                "App::PropertyBool",
			                "user_location",
			                "Punch",
			                ).user_location = False
		#obj.addProperty("App::PropertyEnumeration", "ds", "Shear_Steel", "")
		#obj.addProperty("App::PropertyEnumeration", "Fys", "Shear_Steel", "")
		#obj.ds = ['8', '10', '12', '14', '16', '18', '20']
		#obj.Fys = ['340', '400']
		obj.setEditorMode("text", 2)
		obj.setEditorMode("center_of_punch", 2)
		obj.setEditorMode("Area", 2)
		obj.setEditorMode("faces", 2)

	def get_user_location_faces(self, faces, location):

		normals = self._location[location]
		if len(normals) >= len(faces):
			return faces
		new_faces = []
		for f in faces:
			normal = tuple(f.normalAt(0, 0))
			if normal in normals:
				new_faces.append(f)
		return new_faces

	def onDocumentRestored(self, obj):
		obj.Proxy = self
		self.set_properties(obj)

	def execute(self, obj):
		FreeCAD.Console.PrintMessage("*" * 20 + "\nrunning execute method\n")
		d = obj.foundation.d.Value
		x = obj.bx + d
		y = obj.by + d
		offset_shape = punch_funcs.rectangle_face(obj.center_of_load, x, y)
		edges = punch_funcs.punch_area_edges(obj.foundation.shape, offset_shape)
		faces = punch_funcs.punch_faces(edges, d)
		if obj.user_location:
			faces = self.get_user_location_faces(faces, obj.Location)
		obj.faces = Part.makeCompound(faces)
		obj.Location = punch_funcs.location_of_column(faces)
		obj.alpha_s = self.alphas(obj.Location)
		obj.I22, obj.I33, obj.I23 = punch_funcs.moment_inersia(faces)
		if 'Corner' in obj.Location:
			obj.I23 = 0
		obj.Area = punch_funcs.area(faces)
		obj.center_of_punch = punch_funcs.center_of_mass(faces)
		obj.b0 = punch_funcs.lenght_of_edges(edges)
		obj.d = d
		obj.one_way_shear_capacity, obj.Vc, obj.vc = self.allowable_stress(obj)
		rect = punch_funcs.rectangle_face(obj.center_of_load, obj.bx, obj.by)
		col = rect.extrude(FreeCAD.Vector(0, 0, 4000))
		comp = Part.makeCompound(faces + [col])
		obj.Shape = comp
		self.punch_ratios(obj)
		# ratio = obj.Vu.Value / obj.vc.Value
		# t = f"{ratio:.2f}"
		# print(t, type(t))
		# obj.Ratio = t
		# obj.text.Text = [obj.Location, obj.Ratio]
		return

	def alphas(self, location):
		if 'Interier' in location:
			return 40
		elif 'Edge' in location:
			return 30
		elif 'Corner' in location:
			return 20

	def allowable_stress(self, obj, phi_c=.75):
		b0d = obj.Area
		beta = obj.bx / obj.by
		if beta < 1:
			beta = obj.by / obj.bx
		fc = obj.fc.getValueAs("N/mm^2")
		one_way_shear_capacity = math.sqrt(fc) * b0d / 6 * phi_c
		Vc1 = one_way_shear_capacity * 2
		Vc2 = one_way_shear_capacity * (1 + 2 / beta)
		Vc3 = one_way_shear_capacity * (2 + obj.alpha_s * obj.d / obj.b0) / 2
		Vc = min(Vc1, Vc2, Vc3)
		vc = Vc / (b0d)
		return one_way_shear_capacity, Vc, vc

	def ultimate_shear_stress(self, obj):
		combos = list(obj.combos_load.keys())
		bx = obj.bx
		by = obj.by
		location = obj.Location
		location = location.rstrip('1234').lower()
		gamma_fx = 1 / (1 + (2 / 3) * math.sqrt(by / bx))
		gamma_fy = 1 / (1 + (2 / 3) * math.sqrt(bx / by))
		gamma_vx = 1 - gamma_fx
		gamma_vy = 1 - gamma_fy
		I22 = obj.I22
		I33 = obj.I33
		I23 = obj.I23
		b0d = obj.Area
		x1, y1, _ = obj.center_of_load
		x3, y3, _ = obj.center_of_punch
		combos_Vu = dict()
		for combo, forces in obj.combos_load.items():
			faces_ratio = []
			for f in obj.faces.Faces:
				x4 = f.CenterOfMass.x
				y4 = f.CenterOfMass.y
				vu, mx, my = [float(force) for force in forces.split(",")]
				Vu = vu / b0d + (gamma_vx * (mx - vu * (y3 - y1)) * (I33 * (y4 - y3) - I23 * (x4 - x3))) / (I22 * I33 - I23 ** 2) - (gamma_vy * (my - vu * (x3 - x1)) * (I22 * (x4 - x3) - I23 * (y4 - y3))) / (I22 * I33 - I23 ** 2)
				Vu *= 1000
				faces_ratio.append(Vu)
			max_ratio_in_combo = max(faces_ratio)
			combos_Vu[combo] = f"{max_ratio_in_combo:.2f}"
		# adding maximum value of Vu to combos_Vu
		max_Vu = max([float(vu) for vu in combos_Vu.values()])
		combos_Vu["Max"] = str(max_Vu)
		return combos_Vu

	def punch_ratios(self, obj):
		combos_Vu = self.ultimate_shear_stress(obj)
		obj.one_way_shear_capacity, obj.Vc, obj.vc = self.allowable_stress(obj)
		combos_ratio = dict()
		for combo, Vu in combos_Vu.items():
			ratio = float(Vu) / obj.vc.Value
			combos_ratio[combo] = f"{ratio:.2f}"
		obj.combos_ratio = combos_ratio
		ratio = obj.combos_ratio["Max"]
		obj.Ratio = ratio

	@staticmethod
	def __get_color(pref_intity, color=674321151):
		c = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, color)
		r = float((c >> 24) & 0xFF) / 255.0
		g = float((c >> 16) & 0xFF) / 255.0
		b = float((c >> 8) & 0xFF) / 255.0
		return (r, g, b)


class _ViewProviderPunch:
	def __init__(self, vobj):
		''' Set this object to the proxy object of the actual view provider '''
		#
		vobj.Proxy = self
		# vobj.LineWidth = 1.

	def attach(self, vobj):
		self.ViewObject = vobj
		self.Object = vobj.Object

	def updateData(self, obj, prop):
		''' If a property of the handled feature has changed we have the chance to handle this here '''
		if prop == "Ratio":
			if float(obj.Ratio) == 0:
				return
			ratio = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetFloat("RatioTolerance", 1.0)
			if float(obj.Ratio) > ratio:
				color = get_color("Ratio_above_color", 4278190335)
			else:
				color = get_color("Ratio_below_color", 16711935)
			obj.ViewObject.ShapeColor = color
			if hasattr(obj, "text") and obj.text:
				if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("is_text_color", False):
					color = get_color("text_color", 674321151)
				obj.text.ViewObject.TextColor = color
				obj.text.Text = [obj.Location, obj.Ratio]
		return

	def claimChildren(self):
		children = [self.Object.text]
		return children

	def getDisplayModes(self, obj):
		''' Return a list of display modes. '''
		modes = []
		return modes

	def getDefaultDisplayMode(self):
		''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
		return "Shaded"

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
		rel_path = "Mod/Civil/images/punch.svg"
		icon_path = FreeCAD.ConfigGet("AppHomePath") + rel_path
		import os
		if not os.path.exists(icon_path):
			icon_path = FreeCAD.ConfigGet("UserAppData") + rel_path
		return icon_path

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


def get_color(pref_intity, color=16711935):
	c = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, color)
	r = float((c >> 24) & 0xFF) / 255.0
	g = float((c >> 16) & 0xFF) / 255.0
	b = float((c >> 8) & 0xFF) / 255.0
	return (r, g, b)

# def get_color(pref_intity, default=11247519):
#	 RGBint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, default)
#	 print(RGBint)
#	 b = (RGBint & 255) / 255
#	 g = ((RGBint >> 8) & 255) / 255
#	 r = ((RGBint >> 16) & 255) / 255
#	 return (r, g, b)


def make_punch(
	foundation_plane: Part.Face,
	foun_obj,
	bx: Union[float, int],
	by: Union[float, int],
	center: FreeCAD.Vector,
	combos_load: dict,
	location: str = 'Corner1',
	):

	p = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Punch")
	_Punch(p)
	_ViewProviderPunch(p.ViewObject)
	p.foundation_plane = foundation_plane
	p.foundation = foun_obj
	p.bx = bx
	p.by = by
	p.center_of_load = center
	p.fc = foun_obj.fc
	p.combos_load = combos_load
	p.Location = location

	FreeCAD.ActiveDocument.recompute()

	return p

