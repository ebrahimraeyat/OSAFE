from pathlib import Path
from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD
import Draft

import FreeCADGui as Gui
import draftutils.utils as utils
import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original
import draftguitools.gui_tool_utils as gui_tool_utils
import draftguitools.gui_lines as gui_lines

from draftutils.messages import _msg, _err
from draftutils.translate import translate

from safe.punch import punch_funcs
from safe.punch.base_foundation import make_base_foundation

class BaseFoundation(gui_lines.Line):
    """Gui command for the Base Foundation tool."""

    def __init__(self):
        self.wire = None
        self.obj = None
        super(BaseFoundation, self).__init__(wiremode=True)

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_base_foundation",
            "Create base_foundation")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_base_foundation",
            "Create base_foundation")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "base_foundation.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}
    
    def Activated(self):
        """
        Execute when the command is called.
        """
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        self.bf_width = p.GetFloat("base_foundation_width",1000)
        self.bf_left_width = p.GetFloat("base_foundation_left_width",500)
        self.bf_right_width = p.GetFloat("base_foundation_right_width",500)
        self.bf_align = p.GetString("base_foundation_align",'Center')
        self.bf_height = p.GetFloat("base_foundation_height",1000)
        self.bf_soil_modulus = p.GetFloat("base_foundation_soil_modulus",2)
        self.fc = p.GetFloat("foundation_fc", 25)
        self.layer = p.GetString("base_foundation_layer","A")
        self.base_foundation_ui = self.taskbox()
        selections = Gui.Selection.getSelection()
        if selections:
            wire = selections[0]
            if wire.Proxy.Type == 'Wire':
                self.wire = wire
                # Gui.Control.showDialog(self.base_foundation_ui)
                # self.
            
        super(BaseFoundation, self).Activated(name=translate("OSAFE", "BaseFoundation"))
        self.ui.layout.insertWidget(0, self.base_foundation_ui)
        self.set_layer()
        self.update_gui()

    def action(self, arg):
        """
        Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view
        by the `Activated` method of the parent class.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":  # mouse movement detection
            (self.point,
             ctrlPoint, info) = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()
            self.drawUpdate(self.point)
        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):
            if arg["Position"] == self.pos:
                self.finish(False, cont=True)

            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                (self.point,
                 ctrlPoint, info) = gui_tool_utils.getPoint(self, arg)
            if self.point:
                self.ui.redraw()
                self.pos = arg["Position"]
                self.node.append(self.point)
                self.drawUpdate(self.point)
                if not self.isWire and len(self.node) == 2:
                    self.finish(False, cont=True)
                if len(self.node) > 2:
                    if (self.point - self.node[0]).Length < utils.tolerance():
                        self.undolast()
                        self.finish(True, cont=True)
                        _msg(translate("draft",
                                       "Spline has been closed"))

    def undolast(self):
        """Undo last line segment."""
        import Part
        if len(self.node) > 1:
            self.node.pop()
            # self.linetrack.update(self.node)
            wire = Part.makePolygon(self.node)
            shape = punch_funcs.get_left_right_offset_wire_and_shape(wire, self.bf_left_width, self.bf_right_width)[0]
            self.obj.Shape = shape
            _msg(translate("draft", "Last point has been removed"))

    def drawUpdate(self, point):
        """Draw and update to the spline."""
        import Part
        if self.planetrack and self.node:
            self.planetrack.set(self.node[-1])
        # if len(self.node) == 1:
        #     # self.linetrack.on()
        #     _msg(translate("draft", "Pick next point"))
        # else:
        if len(self.node) > 0:
            if (point - self.node[0]).Length < utils.tolerance():
                return
            wire = Part.makePolygon(self.node + [point])
            shape = punch_funcs.get_left_right_offset_wire_and_shape(wire, self.bf_left_width, self.bf_right_width)[0]
            self.obj.Shape = Part.makeCompound([wire, shape])
            # _msg(translate("draft",
            #                 "Pick next point, "
            #                 "or finish (A) or close (O)"))

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the spline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        fc = self.fc_spin.value()
        soil_modulus = self.soil_modulus_spin.value()
        p.SetFloat("foundation_fc",fc)
        p.SetFloat("base_foundation_soil_modulus",soil_modulus)
        # if self.ui:
            # self.linetrack.finalize()
        if not utils.getParam("UiMode", 1):
            Gui.Control.closeDialog()
        if self.obj:
            # Remove temporary object, if any
            old = self.obj.Name
            todo.ToDo.delay(self.doc.removeObject, old)
        if len(self.node) > 1 or self.wire is not None:
            # The command to run is built as a series of text strings
            # to be committed through the `draftutils.todo.ToDo` class.
            try:
                FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Base Foundation"))
                if self.wire is None:
                    wire = Draft.make_wire(self.node)              
                else:
                    wire = self.wire
                make_base_foundation(wire, self.layer, self.bf_width, self.bf_height, soil_modulus, f'{fc} MPa', self.bf_align, self.bf_left_width, self.bf_right_width)
                FreeCAD.ActiveDocument.commitTransaction()
            except Exception:
                _err("Draft: error delaying commit")

        # `Creator` is the grandfather class, the parent of `Line`;
        # we need to call it to perform final cleanup tasks.
        #
        # Calling it directly like this is a bit messy; maybe we need
        # another method that performs cleanup (superfinish)
        # that is not re-implemented by any of the child classes.
        gui_base_original.Creator.finish(self)
        if self.ui and self.ui.continueMode:
            self.Activated()

    def numericInput(self, numx, numy, numz):
        """Validate the entry fields in the user interface.

        This function is called by the toolbar or taskpanel interface
        when valid x, y, and z have been entered in the input fields.
        """
        self.point = FreeCAD.Vector(numx, numy, numz)
        self.node.append(self.point)
        self.drawUpdate(self.point)
        if not self.isWire and len(self.node) == 2:
            self.finish(False, cont=True)
        self.ui.setNextFocus()

    def taskbox(self):

        "sets up a taskbox widget"
        punch_path = Path(__file__).parent
        w = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'base_foundation.ui'))
    
        self.layer_box = w.strip_layer
        self.width_spinbox = w.width_spinbox
        self.left_width_spinbox = w.left_width_spinbox
        self.right_width_spinbox = w.right_width_spinbox
        self.height_spinbox = w.height_spinbox
        self.align_box = w.align
        self.soil_modulus_spin = w.soil_modulus
        self.fc_spin = w.fc
        # self.layer_box.setValue(self.bx / 10))
        self.width_spinbox.setValue(int(self.bf_width / 10))
        self.left_width_spinbox.setValue(int(self.bf_left_width / 10))
        self.right_width_spinbox.setValue(int(self.bf_right_width / 10))
        self.height_spinbox.setValue(int(self.bf_height / 10))
        self.soil_modulus_spin.setValue(self.bf_soil_modulus)
        self.fc_spin.setValue(self.fc)
        i = self.align_box.findText(self.bf_align)
        self.align_box.setCurrentIndex(i)
        i = self.layer_box.findText(self.layer)
        self.layer_box.setCurrentIndex(i)

        # connect slotsx
        self.width_spinbox.valueChanged.connect(self.set_width)
        self.left_width_spinbox.valueChanged.connect(self.set_width)
        self.right_width_spinbox.valueChanged.connect(self.set_width)
        self.height_spinbox.valueChanged.connect(self.set_height)
        self.align_box.currentIndexChanged.connect(self.set_width)
        self.align_box.currentIndexChanged.connect(self.update_gui)
        self.layer_box.currentIndexChanged.connect(self.set_layer)

        # self.height_spin.valueChanged.connect(self.set_height)
        # self.soil_modulus_spin.valueChanged.connect(self.set_soil_modulus)
        return w

    def update_gui(self):
        align = self.align_box.currentText()
        if align == 'Left':
            self.left_width_spinbox.setEnabled(True)
            self.right_width_spinbox.setEnabled(False)
        elif align == 'Right':
            self.right_width_spinbox.setEnabled(True)
            self.left_width_spinbox.setEnabled(False)
        elif align == 'Center':
            self.right_width_spinbox.setEnabled(False)
            self.left_width_spinbox.setEnabled(False)

    def set_width(self):
        self.bf_width = self.width_spinbox.value() * 10
        align = self.align_box.currentText()
        if align == 'Left':
            sl = self.left_width_spinbox.value() * 10
            sr = self.bf_width - sl
        elif align == 'Right':
            sr = self.right_width_spinbox.value() * 10
            sl = self.bf_width - sr
        elif align == 'Center':
            sr = sl = self.bf_width / 2
        self.left_width_spinbox.setValue(int(sl / 10))
        self.right_width_spinbox.setValue(int(sr / 10))
        self.bf_left_width = sl
        self.bf_right_width = sr
        self.bf_align = align
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        p.SetFloat("base_foundation_width",self.bf_width)
        p.SetFloat("base_foundation_left_width",self.bf_left_width)
        p.SetFloat("base_foundation_right_width",self.bf_right_width)
        p.SetString("base_foundation_align",self.bf_align)
        self.drawUpdate(self.point)

    def set_height(self, d):
        self.bf_height = self.height_spinbox.value() * 10
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetFloat("base_foundation_height",self.bf_height)

    def set_layer(self):
        if self.obj is None:
            return
        self.layer = self.base_foundation_ui.strip_layer.currentText()
        if self.layer == 'A':
            self.obj.ViewObject.ShapeColor = (1.00,0.00,0.20)
        elif self.layer == 'B':
            self.obj.ViewObject.ShapeColor = (0.20,0.00,1.00)
        elif self.layer == 'other':
            self.obj.ViewObject.ShapeColor = (0.20,1.00,0.00)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetString("base_foundation_layer",self.layer)





Gui.addCommand('osafe_base_foundation', BaseFoundation())

## @}
