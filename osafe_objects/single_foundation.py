import math
from typing import Union
from pathlib import Path

import FreeCAD
from FreeCAD import Vector
import Part
import ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import draftguitools.gui_trackers as DraftTrackers
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt


class SingleFoundation(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Footing"
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.Proxy = self
        self.Type = "SingleFoundation"

        if not hasattr(obj, "design_type"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "design_type",
                "Strip",
                "",
                8,
                ).design_type = ['column']
        if not hasattr(obj, "ks"):
            obj.addProperty(
                "App::PropertyFloat",
                "ks",
                "Soil",
                "",
                8,
                )
        if not hasattr(obj, "fc"):
            obj.addProperty(
            "App::PropertyPressure",
            "fc",
            "Concrete",
            "",
            8,
            )
        if not hasattr(obj, "design_layer_a"):
            obj.addProperty(
            "App::PropertyBool",
            "design_layer_a",
            "Design_Layer",
            ).design_layer_a = True
        
        if not hasattr(obj, "design_layer_b"):
            obj.addProperty(
            "App::PropertyBool",
            "design_layer_b",
            "Design_Layer",
            ).design_layer_b = True
        
        if not hasattr(obj, "no_of_design_layer_a"):
            obj.addProperty(
            "App::PropertyInteger",
            "no_of_design_layer_a",
            "Design_Layer",
            ).no_of_design_layer_a = True

        if not hasattr(obj, "no_of_design_layer_b"):
            obj.addProperty(
            "App::PropertyInteger",
            "no_of_design_layer_b",
            "Design_Layer",
            ).no_of_design_layer_b = True

        if not hasattr(obj, "thickness"):
            obj.addProperty(
                "App::PropertyLength",
                "thickness",
                "SingleFoundation",
                )

        if not hasattr(obj, "Bx"):
            obj.addProperty(
                "App::PropertyLength",
                "Bx",
                "SingleFoundation",
                )

        if not hasattr(obj, "By"):
            obj.addProperty(
                "App::PropertyLength",
                "By",
                "SingleFoundation",
                )
        
        if not hasattr(obj, "angle"):
            obj.addProperty(
                "App::PropertyAngle",
                "angle",
                "SingleFoundation",
                )
        
    def onDocumentRestored(self, obj):
        self.set_properties(obj)

    def execute(self, obj):
        # Create box at origin
        sh = Part.makeBox(obj.Bx.Value, obj.By.Value, obj.thickness.Value)
        # Find center of box
        center = FreeCAD.Vector(obj.Bx.Value/2, obj.By.Value/2, obj.thickness.Value)
        # Move box so its center is at origin
        sh.translate(-center)
        # Rotation about center
        sh.rotate(center, FreeCAD.Vector(0,0,1), obj.angle)
        # Set shape
        obj.Shape = sh
        


class ViewProviderSingleFoundation:

    def __init__(self, vobj):

        vobj.Proxy = self
        
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent.parent / "osafe_images" / "single_foundation.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_single_foundation(
    bx: Union[float, str] = '1 m',
    by: Union[float, str] = '1 m',
    thickness: Union[float, str] = '0.5 m',
    angle: float=0,
    soil_modulus : float =2,
    fc : Union[float, str] = '25 MPa',
    design_type : str = 'column',
    design_layer_a : bool = True,
    design_layer_b : bool = True,
    no_of_design_layer_a : int=1,
    no_of_design_layer_b : int=1,
    ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "SingleFoundation")
    SingleFoundation(obj)
    if FreeCAD.GuiUp:
        ViewProviderSingleFoundation(obj.ViewObject)
        obj.ViewObject.PointSize = 1.00
        obj.ViewObject.LineWidth = 1.00
        obj.ViewObject.Transparency = 40
        obj.ViewObject.DisplayMode = "Flat Lines"
        obj.ViewObject.ShapeColor = (0.33,0.67,1.00)
    obj.Bx = bx
    obj.By = by
    obj.thickness = thickness
    obj.angle = angle
    obj.design_type = design_type
    obj.ks = soil_modulus
    obj.fc = fc
    obj.design_layer_a = design_layer_a
    obj.design_layer_b = design_layer_b
    obj.no_of_design_layer_a = no_of_design_layer_a
    obj.no_of_design_layer_b = no_of_design_layer_b
    FreeCAD.ActiveDocument.recompute()
    return obj


class CommandSingleFoundation:

    "SingleFoundation command definition"


    def GetResources(self):
        path = str(Path(__file__).parent.parent / "osafe_images" / "single_foundation.svg")

        return {'Pixmap'  : path,
                'MenuText': QT_TRANSLATE_NOOP("civiltools_singlefoundation","Single Foundation"),
                'Accel': "S, F",
                'ToolTip': QT_TRANSLATE_NOOP("civiltools_singlefoundation","Creates a Single Foundation")}

    def IsActive(self):

        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        self.bx = p.GetFloat("single_foundation_bx",1000)
        self.by = p.GetFloat("single_foundation_by",1000)
        self.thickness = p.GetFloat("single_foundation_thickness",500)
        self.x_offset = p.GetFloat("single_foundation_x_offset",0)
        self.y_offset = p.GetFloat("single_foundation_y_offset",0)
        self.angle = 0
        self.cardinal_point = p.GetFloat("single_foundation_cardinal_point", 5)
        self.bpoint = None
        self.column = None
        # interactive mode
        if hasattr(FreeCAD,"DraftWorkingPlane"):
            direction = FreeCAD.Vector(0, 0, 1)
            FreeCAD.DraftWorkingPlane.setup(direction=direction)

        self.points = []
        self.tracker = DraftTrackers.boxTracker()
        self.tracker.width(self.by)
        self.tracker.length(self.bx)
        self.tracker.height(self.thickness)
        self.tracker.setRotation(FreeCAD.DraftWorkingPlane.getRotation().Rotation)
        self.tracker.on()
        title=translate("OSAFE","Insertion point of single foundation")+":"
        FreeCADGui.Snapper.getPoint(callback=self.getPoint,movecallback=self.update,extradlg=[self.taskbox()],title=title)
        

    def getPoint(self,point=None,obj=None):

        "this function is called by the snapper when it has a 3D point"

        if point is None:
            self.tracker.finalize()
            return
        FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Single Foundation"))
        dx = self.x_offset_input.value() * 10
        dy = self.y_offset_input.value() * 10
        cardinal_dx, cardinal_dy = get_xy_cardinal_point(self.cardinal_point, self.bx, self.by)
        FreeCADGui.doCommand('from osafe_objects import single_foundation')
        FreeCADGui.doCommand(f'single_foundation = single_foundation.make_single_foundation(bx={self.bx}, by={self.by}, thickness={self.thickness}, angle="{self.angle}")')

        # calculate rotation
        rot = FreeCAD.Rotation()
        rot.Angle = math.radians(self.angle)
        delta = FreeCAD.Vector(
                    dx + cardinal_dx - self.bx / 2,
                    dy + cardinal_dy - self.by / 2,
                    -self.thickness)
        # if hasattr(FreeCAD,"DraftWorkingPlane"):
        #     delta = FreeCAD.DraftWorkingPlane.getRotation().multVec(delta)
        delta = rot.multVec(delta)
        point = point.add(delta)

        FreeCADGui.doCommand(f'single_foundation.Placement.Base = FreeCAD.{point}')
        FreeCADGui.doCommand(f'single_foundation.Placement.Rotation = FreeCAD.{rot}')

        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        self.tracker.finalize()
        self.Activated()


    def taskbox(self):

        "sets up a taskbox widget"
        punch_path = Path(__file__).parent.parent
        w = FreeCADGui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'single_foundation.ui'))
    
        self.bx_spin = w.bx_spin
        self.by_spin = w.by_spin
        self.thickness_spin = w.thickness_spin
        self.x_offset_input = w.x_offset_combo
        self.y_offset_input = w.y_offset_combo
        self.angle_input = w.angle
        self.cardinal_1 = w.cardinal_1
        self.cardinal_2 = w.cardinal_2
        self.cardinal_3 = w.cardinal_3
        self.cardinal_4 = w.cardinal_4
        self.cardinal_5 = w.cardinal_5
        self.cardinal_6 = w.cardinal_6
        self.cardinal_7 = w.cardinal_7
        self.cardinal_8 = w.cardinal_8
        self.cardinal_9 = w.cardinal_9
        self.bx_spin.setValue(int(self.bx / 10))
        self.by_spin.setValue(int(self.by / 10))
        self.thickness_spin.setValue(int(self.thickness / 10))
        self.x_offset_input.setValue(int(self.x_offset / 10))
        self.y_offset_input.setValue(int(self.y_offset / 10))
        self.angle_input.setValue(self.angle)
        for radio in (
            self.cardinal_1,
            self.cardinal_2,
            self.cardinal_3,
            self.cardinal_4,
            self.cardinal_5,
            self.cardinal_6,
            self.cardinal_7,
            self.cardinal_8,
            self.cardinal_9,
            ):
            if str(int(self.cardinal_point)) in radio.objectName():
                radio.setChecked(True)
            else:
                radio.setChecked(False) 
            radio.clicked.connect(self.set_cardinal_point)

        # connect slotsx
        self.bx_spin.valueChanged.connect(self.set_bx)
        self.by_spin.valueChanged.connect(self.set_by)
        self.thickness_spin.valueChanged.connect(self.set_thickness)
        # self.angle_input.valueChanged.connect(self.set_angle)
        return w

    def update(self,point,info):

        "this function is called by the Snapper when the mouse is moved"

        if FreeCADGui.Control.activeDialog():
            dx = self.x_offset_input.value() * 10
            dy = self.y_offset_input.value() * 10
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("singlefoundation_x_offset", dx)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("singlefoundation_y_offset", dy)
            self.x_offset = dx
            self.y_offset = dy
            cardinal_dx, cardinal_dy = get_xy_cardinal_point(self.cardinal_point, self.bx, self.by)
            delta = Vector(dx + cardinal_dx, dy + cardinal_dy, self.thickness/2)
            if hasattr(FreeCAD,"DraftWorkingPlane"):
                delta = FreeCAD.DraftWorkingPlane.getRotation().multVec(delta)
            rot = FreeCAD.Rotation()
            pos = point.add(delta)
            self.column = None
            rot.Angle = math.radians(self.angle)
            delta = rot.multVec(delta)
            pos = point.add(delta)
            self.tracker.setRotation(rot)
            self.tracker.pos(pos)
            self.tracker.on()

    def set_bx(self,d):
        self.bx = d * 10
        self.tracker.length(self.bx)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("single_foundation_bx",self.bx)

    def set_by(self,d):
        self.by = d * 10
        self.tracker.width(self.by)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("single_foundation_by",self.by)

    def set_thickness(self,d):
        self.thickness = d * 10
        self.tracker.height(self.thickness)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("single_foundation_thickness",self.thickness)

    def set_cardinal_point(self):
        if self.cardinal_1.isChecked():
            self.cardinal_point = 1
        elif self.cardinal_2.isChecked():
            self.cardinal_point = 2
        elif self.cardinal_3.isChecked():
            self.cardinal_point = 3
        elif self.cardinal_4.isChecked():
            self.cardinal_point = 4
        elif self.cardinal_5.isChecked():
            self.cardinal_point = 5
        elif self.cardinal_6.isChecked():
            self.cardinal_point = 6
        elif self.cardinal_7.isChecked():
            self.cardinal_point = 7
        elif self.cardinal_8.isChecked():
            self.cardinal_point = 8
        elif self.cardinal_9.isChecked():
            self.cardinal_point = 9
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("single_foundation_cardinal_point", self.cardinal_point)

def get_xy_cardinal_point(
    cardinal : int,
    bx: float = 0,
    by: float = 0,
    ):
    x = y = 0
    if cardinal in (1, 4, 7):
        x = bx / 2
    elif cardinal in (3, 6, 9):
        x = - bx / 2
    if cardinal in (7, 8, 9):
        y = - by / 2
    elif cardinal in (1, 2, 3):
        y = by / 2
    return x, y

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('civil_single_foundation',CommandSingleFoundation())