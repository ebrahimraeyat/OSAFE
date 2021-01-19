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
            'Corner1': [(0, 1, 0), (-1, 0, 0)],
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
            obj.addProperty("App::PropertyFloat", "fc", "Punch", "", 1, True)
        if not hasattr(obj, "bx"):
            obj.addProperty("App::PropertyFloat", "bx", "Column", "", 1, True)
        if not hasattr(obj, "by"):
            obj.addProperty("App::PropertyFloat", "by", "Column", "", 1, True)
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
        #obj.addProperty("App::PropertyEnumeration", "ds", "Shear_Steel", "")
        #obj.addProperty("App::PropertyEnumeration", "Fys", "Shear_Steel", "")
        #obj.ds = ['8', '10', '12', '14', '16', '18', '20']
        #obj.Fys = ['340', '400']
        obj.setEditorMode("text", 2)
        obj.setEditorMode("center_of_punch", 2)
        obj.setEditorMode("Area", 2)
        obj.setEditorMode("faces", 2)

    # def onChanged(self, fp, prop):
    #     if prop == 'Location':
    #         loc = fp.Location
    #         fp.alpha_s = self.alphas(loc)
    #         normals = self._location[loc]
    #         if len(normals) >= len(fp.faces):
    #             for f in fp.faces:
    #                 f.ViewObject.Visibility = True
    #             return
    #         for f in fp.faces:
    #             f.ViewObject.Visibility = True
    #             normal = tuple(f.Shape.normalAt(0, 0))
    #             if not normal in normals:
    #                 f.ViewObject.Visibility = False
    #     return

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
        obj.faces = Part.makeCompound(faces)
        obj.Location = punch_funcs.location_of_column(faces)
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
        one_way_shear_capacity = math.sqrt(obj.fc) * b0d / 6 * phi_c
        Vc1 = one_way_shear_capacity * 2
        Vc2 = one_way_shear_capacity * (1 + 2 / beta)
        Vc3 = one_way_shear_capacity * (2 + obj.alpha_s * obj.d / obj.b0) / 2
        Vc = min(Vc1, Vc2, Vc3)
        vc = Vc / (b0d)
        return one_way_shear_capacity, Vc, vc


class _ViewProviderPunch:
    def __init__(self, vobj):
        ''' Set this object to the proxy object of the actual view provider '''
        #
        vobj.Proxy = self
        # vobj.LineWidth = 1.

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        if prop == "Ratio":
            if float(fp.Ratio) == 0:
                return
            ratio = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetFloat("RatioTolerance", 1.0)
            if float(fp.Ratio) > ratio:
                color = get_color("Ratio_above_color", 4278190335)
            else:
                color = get_color("Ratio_below_color", 16711935)
            fp.ViewObject.ShapeColor = color
            if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("is_text_color", False):
                color = get_color("text_color", 674321151)
            fp.text.ViewObject.TextColor = color
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
#     RGBint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, default)
#     print(RGBint)
#     b = (RGBint & 255) / 255
#     g = ((RGBint >> 8) & 255) / 255
#     r = ((RGBint >> 16) & 255) / 255
#     return (r, g, b)


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
    p.fc = foun_obj.fc.Value
    p.combos_load = combos_load
    p.Location = location

    FreeCAD.ActiveDocument.recompute()

    return p

