import math
from pathlib import Path
from typing import Union
import FreeCAD
import Part
if FreeCAD.GuiUp:
    import FreeCADGui as Gui
    import PySide2

try:
    from safe.punch import punch_funcs
except:
    import punch_funcs


class Punch:
    def __init__(self, obj):
        self.set_properties(obj)
        obj.Location = ['Corner 1', 'Corner 2', 'Corner 3', 'Corner 4',
                        'Edge 1', 'Edge 2', 'Edge 3', 'Edge 4', 'Interior']

    def set_properties(self, obj):
        self.Type = "Punch"
        obj.Proxy = self
        if not hasattr(obj, "text"):
            obj.addProperty(
                "App::PropertyLink",
                "text",
                "Punch",
                )
        if not hasattr(obj, "faces"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "faces",
                "Punch",
                "",
                1,
                False,
                )
        if not hasattr(obj, "d"):
            obj.addProperty(
                "App::PropertyFloat",
                "d",
                "Punch",
                "",
                1,
                True,
                )
        if not hasattr(obj, "Area"):
            obj.addProperty(
                "App::PropertyArea",
                "Area",
                "Punch",
                )
        if not hasattr(obj, "fc"):
            obj.addProperty(
                "App::PropertyPressure",
                "fc",
                "Punch",
                "",
                1,True,
                )
        if not hasattr(obj, "id"):
            obj.addProperty(
                "App::PropertyString",
                "id",
                "Column",
                "",
                1,
                True,
                )
        if not hasattr(obj, "I22"):
            obj.addProperty(
                "App::PropertyFloat",
                "I22",
                "Punch",
                "",
                1,
                True,
                )
        if not hasattr(obj, "I33"):
            obj.addProperty(
                "App::PropertyFloat",
                "I33",
                "Punch",
                "",
                1,
                True,
                )
        if not hasattr(obj, "I23"):
            obj.addProperty(
                "App::PropertyFloat",
                "I23",
                "Punch",
                "",
                1,
                True,
                )
        if not hasattr(obj, "center_of_punch"):
            obj.addProperty("App::PropertyVector",
                "center_of_punch",
                "Punch",
                )
        if not hasattr(obj, "Ratio"):
            obj.addProperty(
                "App::PropertyString",
                "Ratio",
                "Punch",
                "",
                1,
                True,
                ).Ratio = '0.'
        if not hasattr(obj, "Location"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "Location",
                "Punch",
                )
        if not hasattr(obj, "b0"):
            obj.addProperty(
                "App::PropertyFloat",
                "b0",
                "Punch",
                "",
                1,
                True,
                )
        if not hasattr(obj, "alpha_s"):
            obj.addProperty(
                "App::PropertyInteger",
                "alpha_s",
                "Shear_Stress",
                "",
                1,
                True,
                )
        if not hasattr(obj, "one_way_shear_capacity"):
            obj.addProperty(
                "App::PropertyForce",
                "one_way_shear_capacity",
                "Shear_Stress",
                "",
                1,
                True,
                )
        if not hasattr(obj, "Vc"):
            obj.addProperty(
                "App::PropertyForce",
                "Vc",
                "Shear_Stress",
                "Shear Strength of Concrete",
                1,
                True,
                )
        if not hasattr(obj, "vc"):
            obj.addProperty(
                "App::PropertyPressure",
                "vc",
                "Shear_Stress",
                "Shear Stress of Concrete",
                1,
                True,
                ).vc = 1.
        if not hasattr(obj, "Vu"):
            obj.addProperty(
                "App::PropertyForce",
                "Vu",
                "Shear_Stress",
                "The Ultimate two way shear force in critical section",
                1,
                True,
                ).Vu = 0
        
        if not hasattr(obj, "Use_Reinforcement"):
            obj.addProperty(
                "App::PropertyBool",
                "Use_Reinforcement",
                "Reinforcement",
                "If it allowed to use reinforcement for calculating punch",
                ).Use_Reinforcement = False
        if not hasattr(obj, "Fys"):
            obj.addProperty(
                "App::PropertyPressure",
                "Fys",
                "Reinforcement",
                "Stirrup Stress",
                ).Fys = '340 MPa'
        
        if not hasattr(obj, "s"):
            obj.addProperty(
                "App::PropertyLength",
                "s",
                "Reinforcement",
                "Distance Between Stirrups",
                ).s = 0
        if not hasattr(obj, "Av"):
            obj.addProperty(
                "App::PropertyArea",
                "Av",
                "Reinforcement",
                "Total Area of Stirrups",
                ).Av = 400
        
        if not hasattr(obj, "Vs"):
            obj.addProperty(
                "App::PropertyForce",
                "Vs",
                "Reinforcement",
                "Shear Forcing of Stirrups",
                1,
                True,
                ).Vs = 0
        
        if not hasattr(obj, "x"):
            obj.addProperty(
                "App::PropertyLength",
                "x",
                "Reinforcement",
                "Required Length for set shear stirrups",
                )

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
                "Punch",
                )

        if not hasattr(obj, "foundation_plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "foundation_plan",
                "Punch",
                )
        if not hasattr(obj, "rect"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "rect",
                "Punch",
                )

        if not hasattr(obj, "foundation"):
            obj.addProperty(
                "App::PropertyLink",
                "foundation",
                "Foundation",
                )
        if not hasattr(obj, "column"):
            obj.addProperty(
                "App::PropertyLink",
                "column",
                "Column",
                )

        if not hasattr(obj, "center_of_load"):
            obj.addProperty(
                "App::PropertyVector",
                "center_of_load",
                "Column",
                )
        if not hasattr(obj, "center_of_column"):
            obj.addProperty(
                "App::PropertyVector",
                "center_of_column",
                "Column",
                )

        if not hasattr(obj, "user_location"):
            obj.addProperty(
                            "App::PropertyBool",
                            "user_location",
                            "Punch",
                            ).user_location = False

        if not hasattr(obj, "gamma_vx"):
            obj.addProperty(
                            "App::PropertyFloat",
                            "gamma_vx",
                            "Punch",
                            )

        if not hasattr(obj, "gamma_vy"):
            obj.addProperty(
                            "App::PropertyFloat",
                            "gamma_vy",
                            "Punch",
                            )

        if not hasattr(obj, "edges"):
            obj.addProperty(
                            "Part::PropertyPartShape",
                            "edges",
                            "Punch",
                            )
        if not hasattr(obj, "angle"):
            obj.addProperty(
            "App::PropertyAngle",
            "angle",
            "Column",
            )
        if not hasattr(obj, "bx"):
            obj.addProperty(
            "App::PropertyFloat",
            "bx",
            "Column",
            )
        if not hasattr(obj, "by"):
            obj.addProperty(
            "App::PropertyFloat",
            "by",
            "Column",
            )
        if not hasattr(obj, "Messages"):
            obj.addProperty(
                "App::PropertyString",
                "Messages",
                "Message",
                )

        

        #obj.addProperty("App::PropertyEnumeration", "ds", "Shear_Steel", "")
        #obj.addProperty("App::PropertyEnumeration", "Fys", "Shear_Steel", "")
        #obj.ds = ['8', '10', '12', '14', '16', '18', '20']
        #obj.Fys = ['340', '400']
        obj.setEditorMode("text", 2)
        obj.setEditorMode("center_of_punch", 2)
        # obj.setEditorMode("Area", 2)
        obj.setEditorMode("faces", 2)
        obj.setEditorMode("Messages", 1)

    def onDocumentRestored(self, obj):
        self.set_properties(obj)

    def execute(self, obj):
        d = obj.foundation.d.Value
        obj.fc = obj.foundation.fc
        # try to find base plate if column is steel
        obj.angle = math.degrees(obj.column.Placement.Rotation.Angle) - 90
        base_plate = None
        inlist = obj.column.InList
        if inlist:
            for o in inlist:
                if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BasePlate':
                    base_plate = o
                    break
        colbb = obj.column.Shape.BoundBox
        if base_plate:
            bpbb = base_plate.Shape.BoundBox
            center = bpbb.Center.add(colbb.Center) / 2
            obj.bx = (base_plate.Bx + obj.column.Base.Height).Value / 2
            obj.by = (base_plate.By + obj.column.Base.Width).Value / 2
        else:
            center = colbb.Center
            if hasattr(obj.column.Base, 'Radius'):
                obj.bx = obj.by = math.sqrt(obj.column.Base.Area.Value)
            else:
                obj.bx = obj.column.Base.Height.Value
                obj.by = obj.column.Base.Width.Value
        load_center = colbb.Center
        obj.center_of_load = FreeCAD.Vector(load_center.x, load_center.y, colbb.ZMin)
        obj.center_of_column = FreeCAD.Vector(center.x, center.y, colbb.ZMin)
        x = obj.bx + d
        y = obj.by + d
        offset_shape = punch_funcs.rectangle_face(obj.center_of_column, x, y)
        foun_plan = obj.foundation.plan.copy()
        if obj.angle != 0:
            foun_plan.rotate(
                obj.center_of_column,
                FreeCAD.Vector(0, 0, 1),
                -obj.angle.Value,
                )
        edges = punch_funcs.punch_area_edges(foun_plan, offset_shape)
        faces = punch_funcs.punch_faces(edges, d)
        if obj.user_location:
            faces = punch_funcs.get_user_location_faces(faces, obj.Location)
        obj.Location = punch_funcs.location_of_column(faces)
        obj.alpha_s = self.alphas(obj.Location)
        obj.I22, obj.I33, obj.I23 = punch_funcs.moment_inertia(faces)
        if 'Corner' in obj.Location:
            obj.I23 = 0
        obj.Area = f"{punch_funcs.area(faces)} mm^2"
        obj.center_of_punch = punch_funcs.center_of_mass(faces)
        obj.b0 = punch_funcs.length_of_edges(edges)
        obj.gamma_vx, obj.gamma_vy = punch_funcs.gamma_v(obj.bx, obj.by)
        obj.d = d
        self.allowable_stress(obj)
        edges = Part.makeCompound(edges)
        if obj.angle != 0:
            obj.edges = edges.rotate(
                obj.center_of_column,
                FreeCAD.Vector(0, 0, 1),
                obj.angle.Value,
                )
        else:
            obj.edges = edges
        # faces = Part.makeCompound(faces)
        rect = punch_funcs.rectangle_face(obj.center_of_column, obj.bx, obj.by)
        if obj.angle.Value != 0:
            rect.rotate(
                obj.center_of_column,
                FreeCAD.Vector(0, 0, 1),
                obj.angle.Value,
            )
        obj.rect = rect
        obj.faces = Part.makeCompound(faces)
        if obj.angle.Value != 0:
            faces = [f.rotate(
                    obj.center_of_column,
                    FreeCAD.Vector(0, 0, 1),
                    obj.angle.Value,
                ) for f in faces]
        comp = Part.makeCompound(faces + [obj.rect])
        obj.Shape = comp
        self.punch_ratios(obj)

        # calculate stirrups
        if float(obj.Ratio) > 1.0:
            obj.Use_Reinforcement = True
            
        # if obj.Use_Reinforcement:
            Av_over_s = (obj.Vu / 0.75 - obj.Vc) / (obj.Fys * obj.foundation.d)
            obj.s = max(0, obj.Av / Av_over_s)
            obj.Vs = obj.Av * obj.Fys * obj.foundation.d / obj.s
            # calculate required length for arranging stirrups
            Vu = obj.Vu.getValueAs('N').Value
            fc = obj.fc.getValueAs('MPa').Value
            b0_prim = Vu * 6 / (math.sqrt(fc) * obj.d)
            if "Corner" in obj.Location:
                n = 4
            elif "Edge" in obj.Location:
                n = 2
            elif obj.Location == "Interior":
                n = 1
            x = n * b0_prim / (2 * math.pi) - obj.d / 2
            if x > 0:
                obj.x = f"{x} mm"
            else:
                obj.x = 0
        if obj.Vs > 2 * obj.Vc:
            # text = '<html> <span style=" font-size:9pt; font-weight:600; color:#FF0000;">Vs is greater than 2 * Vc</span>'
            text = 'Vs > 2 * Vc'
            obj.Messages = text
        else:
            obj.Messages = ""


    def alphas(self, location):
        if 'Interior' in location:
            return 40
        elif 'Edge' in location:
            return 30
        elif 'Corner' in location:
            return 20

    def allowable_stress(self, obj, phi_c=.75):
        b0d = obj.Area.getValueAs('mm^2').Value
        beta = obj.bx / obj.by
        if beta < 1:
            beta = obj.by / obj.bx
        fc = obj.fc.getValueAs("N/mm^2").Value
        obj.one_way_shear_capacity = f"{math.sqrt(fc) * b0d / 6 * phi_c} N"
        Vc1 = obj.one_way_shear_capacity * 2
        Vc2 = obj.one_way_shear_capacity * (1 + 2 / beta)
        Vc3 = obj.one_way_shear_capacity * (2 + obj.alpha_s * obj.d / obj.b0) / 2
        obj.Vc = min(Vc1, Vc2, Vc3)
        obj.vc = obj.Vc / (obj.Area)
        return obj.one_way_shear_capacity, obj.Vc, obj.vc

    def ultimate_shear_stress(self, obj):
        location = obj.Location
        location = location.rstrip('1234').lower()
        I22 = obj.I22
        I33 = obj.I33
        I23 = obj.I23
        b0d = obj.Area.getValueAs('mm^2').Value
        x1, y1, _ = obj.center_of_load
        x3, y3, _ = obj.center_of_punch
        combos_Vu = dict()
        for combo, forces in obj.column.combos_load.items():
            faces_ratio = []
            for f in obj.faces.Faces:
                x4 = f.CenterOfMass.x
                y4 = f.CenterOfMass.y
                vu, mx, my = [float(force) for force in forces.split(",")]
                Vu = vu / b0d + \
                    (obj.gamma_vx * (mx - vu * (y3 - y1)) * (I33 * (y4 - y3) - I23 * (x4 - x3))) / (I22 * I33 - I23 ** 2) - \
                    (obj.gamma_vy * (my - vu * (x3 - x1)) * (I22 * (x4 - x3) - I23 * (y4 - y3))) / (I22 * I33 - I23 ** 2)
                Vu *= 1000
                faces_ratio.append(Vu)
            max_ratio_in_combo = max(faces_ratio)
            combos_Vu[combo] = f"{max_ratio_in_combo:.2f}"
        # adding maximum value of Vu to combos_Vu
        max_Vu = max([float(vu) for vu in combos_Vu.values()])
        combos_Vu["Max"] = str(max_Vu)
        # max_Vu is shear stress, we multiply it with punch area to get ultimate shear force
        obj.Vu = f"{max_Vu * b0d} N"
        return combos_Vu

    def punch_ratios(self, obj):
        combos_Vu = self.ultimate_shear_stress(obj)
        combos_ratio = dict()
        for combo, Vu in combos_Vu.items():
            ratio = float(Vu) / obj.vc.getValueAs('MPa').Value
            combo_name = combo.split()[0]
            current_ratio = combos_ratio.get(combo_name, 0)
            ratio = max(float(current_ratio), ratio)
            combos_ratio[combo_name] = f"{ratio:.2f}"
        obj.combos_ratio = combos_ratio
        ratio = obj.combos_ratio["Max"]
        obj.Ratio = ratio

    @staticmethod
    def __get_color(pref_intity, color=674321151):
        c = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, color)
        r = float((c >> 24) & 0xFF) / 255.0
        g = float((c >> 16) & 0xFF) / 255.0
        b = float((c >> 8) & 0xFF) / 255.0
        return (r, g, b)


class ViewProviderPunch:
    def __init__(self, vobj):
        ''' Set this object to the proxy object of the actual view provider '''
        vobj.Proxy = self
        vobj.LineWidth = 1.
        vobj.PointSize = 1.

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def onDelete(self, vobj, subelements):
        if vobj.Object.text:
            FreeCAD.ActiveDocument.removeObject(vobj.Object.text.Name)
        return True

    def setEdit(self, vobj, mode=0):
        obj = vobj.Object
        ui = Ui(obj)
        ui.setupUi()
        Gui.Control.showDialog(ui)
        return True
    
    def unsetEdit(self, vobj, mode):
        Gui.Control.closeDialog()
        return
        
    def doubleClicked(self,vobj):
        self.setEdit(vobj)

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
                if hasattr(obj.text.ViewObject, "TextColor"):
                    obj.text.ViewObject.TextColor = color
                obj.text.Text = [obj.Location, obj.Ratio]

                self.set_text_placement(obj)
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
        return "Flat Lines"

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
        and if not defined, a default icon is shown.
        '''
        return str(Path(__file__).parent / "Resources" / "icons" / "punch.svg")

    def __getstate__(self):
        ''' When saving the document, this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.
        '''
        return None

    def __setstate__(self, state):
        ''' When restoring the pickled object from document we have the chance to set some
        internals here. Since no data were pickled nothing needs to be done here.
        '''
        return None

    def set_text_placement(self, obj):
        xs = {
                'Corner 1': 'bb.XMin',
                'Corner 2': 'bb.XMax',
                'Corner 3': 'bb.XMax',
                'Corner 4': 'bb.XMin',
                'Edge 1': 'bb.Center.x',
                'Edge 2': 'bb.XMax',
                'Edge 3': 'bb.Center.x',
                'Edge 4': 'bb.XMin',
                'Interior': 'bb.Center.x',
              }
        ys = {
                'Corner 1': 'bb.Center.y',
                'Corner 2': 'bb.Center.y',
                'Corner 3': 'bb.Center.y',
                'Corner 4': 'bb.Center.y',
                'Edge 1': 'bb.YMin',
                'Edge 2': 'bb.Center.y',
                'Edge 3': 'bb.YMax',
                'Edge 4': 'bb.Center.y',
                'Interior': 'bb.YMax',
              }

        justifications = {
                'Corner 1': 'Right',
                'Corner 2': 'Left',
                'Corner 3': 'Left',
                'Corner 4': 'Right',
                'Edge 1': 'Center',
                'Edge 2': 'Left',
                'Edge 3': 'Center',
                'Edge 4': 'Right',
                'Interior': 'Center',
              }
        bb = obj.Shape.BoundBox
        location = obj.Location
        obj.text.Placement.Base.x = eval(xs[location])
        obj.text.Placement.Base.y = eval(ys[location])
        rot = FreeCAD.Rotation()
        rot.Angle = obj.angle.Value * math.pi / 180
        obj.text.Placement.Rotation = rot
        if hasattr(obj.text.ViewObject, "Justification"):
            obj.text.ViewObject.Justification = justifications[location]
        if location in ("Edge 3", "Interior"):
            if hasattr(obj.text.ViewObject, "LineSpacing"):
                obj.text.ViewObject.LineSpacing = -1.00

class Ui:
    def __init__(self, punch_obj=None):
        import os
        self.form = Gui.PySideUic.loadUi(os.path.join(
            os.path.dirname(__file__), 'Resources/ui/column.ui'))
        self.punch_obj = punch_obj

    def setupUi(self):
        self.fill_form(self.punch_obj)

    def fill_form(self, punch_obj):
        location = punch_obj.Location
        index = self.form.location.findText(location)
        bx = punch_obj.bx
        by = punch_obj.by
        user_modified = punch_obj.user_location

        self.form.location.setCurrentIndex(index)
        self.form.bx.setValue(int(bx))
        self.form.by.setValue(int(by))
        if user_modified:
            self.form.user_modified.setCheckState(PySide2.QtCore.Qt.Checked)
        else:
            self.form.user_modified.setCheckState(PySide2.QtCore.Qt.Unchecked)

    def accept(self):
        self.modify_punch()
        self.punch_obj.recompute(True)
        Gui.Control.closeDialog()

    def reject(self):
        Gui.Control.closeDialog()

    def modify_punch(self):
        self.punch_obj.Location = self.form.location.currentText()
        self.punch_obj.user_location = self.form.user_modified.isChecked()
        self.punch_obj.bx = float(self.form.bx.value())
        self.punch_obj.by = float(self.form.by.value())


def get_color(pref_intity, color=16711935):
    c = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, color)
    r = float((c >> 24) & 0xFF) / 255.0
    g = float((c >> 16) & 0xFF) / 255.0
    b = float((c >> 8) & 0xFF) / 255.0
    return (r, g, b)

def make_punch(
    # foundation_plan: Part.Face,
    foun_obj,
    column,
    location: str = 'Corner 1',
    ):

    p = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Punch")
    Punch(p)
    if FreeCAD.GuiUp:
        ViewProviderPunch(p.ViewObject)
    # p.foundation_plan = foundation_plan
    p.foundation = foun_obj
    p.column = column
    p.fc = foun_obj.fc
    p.Location = location
    FreeCAD.ActiveDocument.recompute()
    return p

if __name__ == '__main__':
    doc = FreeCAD.ActiveDocument
    foun = doc.Foundation
    col = Gui.Selection.getSelection()[0]
    make_punch(foun_obj=foun, column=col)

