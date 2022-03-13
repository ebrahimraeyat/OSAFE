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
        obj.column = column
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
        dx = float(self.x_offset_input.text().split()[0])
        dy = float(self.y_offset_input.text().split()[0])
        delta = FreeCAD.Vector(dx-self.bx/2,dy-self.by/2,0)
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
    
        w = QtGui.QWidget()
        ui = FreeCADGui.UiLoader()
        w.setWindowTitle(translate("Arch","BasePlate Dimentions"))
        grid = QtGui.QGridLayout(w)


        # bx
        label1 = QtGui.QLabel(translate("OSAFE","Bx"))
        self.vLength = ui.createWidget("Gui::InputField")
        self.vLength.setText(FreeCAD.Units.Quantity(self.bx,FreeCAD.Units.Length).UserString)
        grid.addWidget(label1,0,0,1,1)
        grid.addWidget(self.vLength,0,1,1,1)

        # by
        label2 = QtGui.QLabel(translate("OSAFE","By"))
        self.vWidth = ui.createWidget("Gui::InputField")
        self.vWidth.setText(FreeCAD.Units.Quantity(self.by,FreeCAD.Units.Length).UserString)
        grid.addWidget(label2,1,0,1,1)
        grid.addWidget(self.vWidth,1,1,1,1)

        # thickness
        label3 = QtGui.QLabel(translate("OSAFE","Thickness"))
        self.vHeight = ui.createWidget("Gui::InputField")
        self.vHeight.setText(FreeCAD.Units.Quantity(self.thickness,FreeCAD.Units.Length).UserString)
        grid.addWidget(label3,2,0,1,1)
        grid.addWidget(self.vHeight,2,1,1,1)
        # offset x
        label4 = QtGui.QLabel(translate("OSAFE","X Offset"))
        self.x_offset_input = ui.createWidget("Gui::InputField")
        self.x_offset_input.setText(FreeCAD.Units.Quantity(self.x_offset,FreeCAD.Units.Length).UserString)
        grid.addWidget(label4,3,0,1,1)
        grid.addWidget(self.x_offset_input,3,1,1,1)
        # offset x
        label5 = QtGui.QLabel(translate("OSAFE","Y Offset"))
        self.y_offset_input = ui.createWidget("Gui::InputField")
        self.y_offset_input.setText(FreeCAD.Units.Quantity(self.y_offset,FreeCAD.Units.Length).UserString)
        grid.addWidget(label5,4,0,1,1)
        grid.addWidget(self.y_offset_input,4,1,1,1)

        # connect slots
        QtCore.QObject.connect(self.vLength,QtCore.SIGNAL("valueChanged(double)"),self.set_bx)
        QtCore.QObject.connect(self.vWidth,QtCore.SIGNAL("valueChanged(double)"),self.set_by)
        QtCore.QObject.connect(self.vHeight,QtCore.SIGNAL("valueChanged(double)"),self.set_thickness)
        # QtCore.QObject.connect(self.x_offset_input,QtCore.SIGNAL("valueChanged(double)"),self.set_pos)
        # QtCore.QObject.connect(self.y_offset_input,QtCore.SIGNAL("valueChanged(double)"),self.set_pos)
        # QtCore.QObject.connect(value4,QtCore.SIGNAL("stateChanged(int)"),self.setContinue)

        # restore preset
        return w

    def update(self,point,info):

        "this function is called by the Snapper when the mouse is moved"

        if FreeCADGui.Control.activeDialog():
            dx = float(self.x_offset_input.text().split()[0])
            dy = float(self.y_offset_input.text().split()[0])
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_x_offset",dx)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_y_offset",dy)
            self.x_offset = dx
            self.y_offset = dy
            delta = Vector(dx, dy, self.thickness/2)
            if hasattr(FreeCAD,"DraftWorkingPlane"):
                delta = FreeCAD.DraftWorkingPlane.getRotation().multVec(delta)
            self.tracker.pos(point.add(delta))
            self.tracker.on()

    def set_bx(self,d):
        self.bx = d
        self.tracker.length(d)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_bx",d)

    def set_thickness(self,d):
        self.thickness = d
        self.tracker.height(d)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_thickness",d)

    def set_by(self,d):
        self.by = d
        self.tracker.width(d)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("baseplate_by",d)

    # def setContinue(self,i):
    #     self.continueCmd = bool(i)
    #     if hasattr(FreeCADGui,"draftToolBar"):
    #         FreeCADGui.draftToolBar.continueMode = bool(i)

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('civil_base_plate',CommandBasePlate())