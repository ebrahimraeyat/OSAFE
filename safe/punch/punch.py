
import Part
import FreeCAD
import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP


class _Punch:
    def __init__(self, obj):
        obj.Proxy = self
        self._location = {
            'Corner1': [(0, -1, 0), (-1, 0, 0)],
            'Corner2': [(0, -1, 0), (1, 0, 0)],
            'Corner3': [(0, 1, 0), (1, 0, 0)],
            'Corner4': [(0, 1, 0), (-1, 0, 0)],
            'Edge1': [(0, -1, 0), (-1, 0, 0), (1, 0, 0)],
            'Edge2': [(0, -1, 0), (1, 0, 0), (0, 1, 0)],
            'Edge3': [(0, 1, 0), (1, 0, 0), (-1, 0, 0)],
            'Edge4': [(0, 1, 0), (-1, 0, 0), (0, -1, 0)],
            'Interier': [(0, 1, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0)]
        }
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.addProperty("App::PropertyLink", "text", "Punch")
        obj.addProperty("App::PropertyLinkList", "faces", "Punch", "", 1, False)
        obj.addProperty("App::PropertyFloat", "d", "Punch", "", 1, True)
        obj.addProperty("App::PropertyVectorList", "normals", "Punch", "", 1, False)
        obj.addProperty("App::PropertyFloat", "Area", "Punch")
        obj.addProperty("App::PropertyInteger", "fc", "Punch", "", 1, True)
        obj.addProperty("App::PropertyFloat", "bx", "Column", "", 1, True)
        obj.addProperty("App::PropertyFloat", "by", "Column", "", 1, True)
        obj.addProperty("App::PropertyInteger", "number", "Column", "", 1, True)
        obj.addProperty("App::PropertyFloat", "I22", "Punch", "", 1, True)
        obj.addProperty("App::PropertyFloat", "I33", "Punch", "", 1, True)
        obj.addProperty("App::PropertyFloat", "I23", "Punch", "", 1, True)
        obj.addProperty("App::PropertyFloat", "x3", "Punch")
        obj.addProperty("App::PropertyFloat", "y3", "Punch")
        obj.addProperty("App::PropertyString", "Ratio", "Punch", "", 1, True).Ratio = '0.'
        obj.addProperty("App::PropertyEnumeration", "Location", "Punch")
        obj.addProperty("App::PropertyFloat", "b0", "Punch", "", 1, True)
        obj.Location = ['Corner1', 'Corner2', 'Corner3', 'Corner4', 'Edge1', 'Edge2', 'Edge3', 'Edge4', 'Interier']
        obj.setEditorMode("text", 2)
        obj.setEditorMode("x3", 2)
        obj.setEditorMode("y3", 2)
        obj.setEditorMode("Area", 2)
        obj.setEditorMode("faces", 2)

    def onChanged(self, fp, prop):
        if prop == 'Location':
            loc = fp.Location
            normals = self._location[loc]
            if len(normals) >= len(fp.faces):
                for f in fp.faces:
                    f.ViewObject.Visibility = True
                return
            for f in fp.faces:
                f.ViewObject.Visibility = True
                normal = tuple(f.Shape.normalAt(0, 0))
                if not normal in normals:
                    f.ViewObject.Visibility = False
        return

    def execute(self, obj):
        obj.I22, obj.I33, obj.I23 = self.moment_inersia(obj)
        obj.Area = self._area(obj)
        obj.x3, obj.y3, _ = self.center_of_mass(obj)
        obj.b0 = self.get_b0(obj)
        obj.d = obj.Area / obj.b0
        return

    def get_b0(self, obj):
        b0 = 0
        for f in obj.faces:
            if f.ViewObject.isVisible():
                for e in f.Shape.Edges:
                    if e.BoundBox.ZLength == 0:
                        b0 += e.Length
                        break
        return b0

    def _area(self, obj):
        area = 0
        for f in obj.faces:
            if f.ViewObject.Visibility == False:
                continue
            f = f.Shape
            area += f.Area
        return area

    def center_of_mass(self, obj):
        '''
        give a shell and return center of mass coordinate
        in (x, y, z)
        '''
        sorat_x = 0
        sorat_y = 0
        sorat_z = 0
        makhraj = 0

        for f in obj.faces:
            if f.ViewObject.Visibility == False:
                continue
            f = f.Shape
            area = f.Area
            x = f.CenterOfMass.x
            y = f.CenterOfMass.y
            z = f.CenterOfMass.z
            sorat_x += area * x
            sorat_y += area * y
            sorat_z += area * z
            makhraj += area
        obj.Area = makhraj
        if makhraj == 0:
            return None
        return (sorat_x / makhraj, sorat_y / makhraj, sorat_z / makhraj)

    def moment_inersia(self, obj):
        '''
        return rotational moment inersia of shell Ixx, Iyy
        '''
        Ixx = 0
        Iyy = 0
        Ixy = 0
        if not self.center_of_mass(obj):
            return 0, 0, 0
        x_bar, y_bar, z_bar = self.center_of_mass(obj)
        for f in obj.faces:
            if f.ViewObject.Visibility == False:
                continue
            f = f.Shape
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
        if 'Corner' in obj.Location:
            Ixy = 0
        return Ixx, Iyy, Ixy


class _ViewProviderPunch:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        #
        obj.Proxy = self

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        return

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
