from os.path import join, dirname, abspath
from typing import Union
from pathlib import Path

import FreeCAD
from FreeCAD import Vector
import Part
import DraftVecUtils

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from PySide2.QtCore import QT_TRANSLATE_NOOP
    import draftguitools.gui_trackers as DraftTrackers
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt


class BasePlate:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "BasePlate"
        self.set_properties(obj)

    def set_properties(self, obj):

        if not hasattr(obj, "Thickness"):
            obj.addProperty(
                "App::PropertyLength",
                "Thickness",
                "BasePlate",
                )

        if not hasattr(obj, "Bx"):
            obj.addProperty(
                "App::PropertyLength",
                "Bx",
                "BasePlate",
                )

        if not hasattr(obj, "By"):
            obj.addProperty(
                "App::PropertyLength",
                "By",
                "BasePlate",
                )
        
        if not hasattr(obj, "Column"):
            obj.addProperty(
                "App::PropertyLink",
                "Column",
                "BasePlate",
                )

    def onDocumentRestored(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def execute(self, obj):
        sh = Part.makeBox(obj.Bx.Value, obj.By.Value, obj.Thickness.Value)
        obj.Shape = sh


class ViewProviderBasePlate:

    def __init__(self, vobj):

        vobj.Proxy = self
        vobj.Transparency = 40
        vobj.DisplayMode = "Flat Lines"


    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "base_plate.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None



def make_base_plate(
    bx: Union[float, str] = '500 mm',
    by: Union[float, str] = '500 mm',
    thickness: Union[float, str] = '2 cm',
    column = None
    ):
    if not column:
        sel = FreeCADGui.Selection.getSelection()
        if sel:
            for col in sel:
                if hasattr(col, 'IfcType') and col.IfcType == 'Column':
                    column = col
                    break
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "BasePlate")
    BasePlate(obj)
    if FreeCAD.GuiUp:
        ViewProviderBasePlate(obj.ViewObject)
    obj.Bx = bx
    obj.By = by
    obj.Thickness = thickness
    if column:
        obj.Column = column
    FreeCAD.ActiveDocument.recompute()
    return obj






class CommandBasePlate:

    "Baseplate command definition"


    def GetResources(self):
        path = str(Path(__file__).parent / "Resources" / "icons" / "base_plate.svg")

        return {'Pixmap'  : path,
                'MenuText': QT_TRANSLATE_NOOP("civiltools_baseplate","Base Plate"),
                'Accel': "B, P",
                'ToolTip': QT_TRANSLATE_NOOP("civiltools_baseplate","Creates a Base Plate")}

    def IsActive(self):

        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        self.bx = p.GetFloat("baseplate_bx",500)
        self.by = p.GetFloat("baseplate_by",500)
        self.thickness = p.GetFloat("baseplate_thickness",10)
        self.x_offset = p.GetFloat("baseplate_x_offset",0)
        self.y_offset = p.GetFloat("baseplate_y_offset",0)
        self.cardinal_point = p.GetFloat("baseplate_cardinal_point", 5)
        # self.continueCmsd = False
        self.bpoint = None
        sel = FreeCADGui.Selection.getSelection()
        # if sel:
        #     FreeCAD.ActiveDocument.openTransaction(translate("civiltools","Create Base Plate"))
        #     FreeCADGui.addModule("Arc")
        #     for obj in sel:
        #         FreeCADGui.doCommand("obj = Arch.makeStructure(FreeCAD.ActiveDocument." + obj.Name + ")")
        #         FreeCADGui.addModule("Draft")
        #         FreeCADGui.doCommand("Draft.autogroup(obj)")
        #     FreeCAD.ActiveDocument.commitTransaction()
        #     FreeCAD.ActiveDocument.recompute()
        #     return

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
        title=translate("OSAFE","Insertion point of base plate")+":"
        FreeCADGui.Snapper.getPoint(callback=self.getPoint,movecallback=self.update,extradlg=[self.taskbox()],title=title)

    def getPoint(self,point=None,obj=None):

        "this function is called by the snapper when it has a 3D point"

        if point is None:
            self.tracker.finalize()
            return
        # if self.bpoint is None:
        #     self.bpoint = point
        #     FreeCADGui.Snapper.getPoint(last=point,callback=self.getPoint,movecallback=self.update,extradlg=[self.taskbox(),self.precast.form,self.dents.form],title=translate("Arch","Next point")+":",mode="line")
        #     return
        self.tracker.finalize()
        FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Base Plate"))
        dx = self.x_offset_input.value() * 10
        dy = self.y_offset_input.value() * 10
        cardinal_dx, cardinal_dy = self.get_xy_cardinal_point(self.cardinal_point)
        delta = FreeCAD.Vector(
                    dx + cardinal_dx - self.bx / 2,
                    dy + cardinal_dy - self.by / 2,
                    0)
        if hasattr(FreeCAD,"DraftWorkingPlane"):
            delta = FreeCAD.DraftWorkingPlane.getRotation().multVec(delta)
        point = point.add(delta)
        FreeCADGui.doCommand('from safe.punch import base_plate')
        FreeCADGui.doCommand(f'bp = base_plate.make_base_plate(bx={self.bx}, by={self.by}, thickness={self.thickness})')

        # calculate rotation
        FreeCADGui.doCommand('bp.Placement.Base = '+DraftVecUtils.toString(point))
        FreeCADGui.doCommand('bp.Placement.Rotation = bp.Placement.Rotation.multiply(FreeCAD.DraftWorkingPlane.getRotation().Rotation)')
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        # if self.continueCmd:
        self.Activated()


    def taskbox(self):

        "sets up a taskbox widget"
        punch_path = Path(__file__).parent
        w = FreeCADGui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'base_plate.ui'))
    
        self.bx_spin = w.bx_spin
        self.by_spin = w.by_spin
        self.thickness_spin = w.thickness_spin
        self.x_offset_input = w.x_offset_combo
        self.y_offset_input = w.y_offset_combo
        # self.cardinal_point_combo = w.cardinal_point_combo
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
        self.thickness_spin.setValue(self.thickness)
        self.x_offset_input.setValue(int(self.x_offset / 10))
        self.y_offset_input.setValue(int(self.y_offset / 10))
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
        return w

    def update(self,point,info):

        "this function is called by the Snapper when the mouse is moved"

        if FreeCADGui.Control.activeDialog():
            dx = self.x_offset_input.value() * 10
            dy = self.y_offset_input.value() * 10
            # cardinal_point = self.cardinal_point_combo.currentIndex() + 1
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_x_offset", dx)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_y_offset", dy)
            # FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_cardinal_point", cardinal_point)
            self.x_offset = dx
            self.y_offset = dy
            # self.cardinal_point = cardinal_point
            cardinal_dx, cardinal_dy = self.get_xy_cardinal_point(self.cardinal_point)
            delta = Vector(dx + cardinal_dx, dy + cardinal_dy, self.thickness/2)
            if hasattr(FreeCAD,"DraftWorkingPlane"):
                delta = FreeCAD.DraftWorkingPlane.getRotation().multVec(delta)
            self.tracker.pos(point.add(delta))
            self.tracker.on()

    def set_bx(self,d):
        self.bx = d * 10
        self.tracker.length(self.bx)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_bx",self.bx)

    def set_by(self,d):
        self.by = d * 10
        self.tracker.width(self.by)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_by",self.by)

    def set_thickness(self,d):
        self.thickness = d
        self.tracker.height(self.thickness)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_thickness",self.thickness)

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
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_cardinal_point", self.cardinal_point)


    # def setContinue(self,i):
    #     self.continueCmd = bool(i)
    #     if hasattr(FreeCADGui,"draftToolBar"):
    #         FreeCADGui.draftToolBar.continueMode = bool(i)

    def get_xy_cardinal_point(self,
        cardinal : int,
        ):
        x = y = 0
        if cardinal in (1, 4, 7):
            x = self.bx / 2
        elif cardinal in (3, 6, 9):
            x = - self.bx / 2
        if cardinal in (7, 8, 9):
            y = - self.by / 2
        elif cardinal in (1, 2, 3):
            y = self.by / 2
        return x, y

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('civil_base_plate',CommandBasePlate())