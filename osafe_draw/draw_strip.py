from pathlib import Path
from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD
import Part
import Draft

import FreeCADGui as Gui
import draftutils.utils as utils
import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original
import draftguitools.gui_tool_utils as gui_tool_utils
import draftguitools.gui_lines as gui_lines

from draftutils.messages import _msg, _err
from draftutils.translate import translate

from osafe_funcs import osafe_funcs
from osafe_objects.strip import make_strip


class DrawStrip(gui_lines.Line):
    """Gui command for Draw Strips."""

    def __init__(self):
        super(DrawStrip, self).__init__(wiremode=True)

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_draw_strip",
            "Draw Strip")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_draw_strip",
            "Draw Strip")
        path = str(
                   Path(__file__).parent.parent / "osafe_images" / "strip.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}
    
    def Activated(self):
        """
        Execute when the command is called.
        """
        super(DrawStrip, self).Activated(name=translate("OSAFE", "DrawStrip"))
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        self.strip_width = p.GetFloat("draw_strip_width",1000)
        self.strip_left_width = p.GetFloat("draw_strip_left_width",500)
        self.strip_right_width = p.GetFloat("draw_strip_right_width",500)
        self.strip_align = p.GetString("draw_strip_align",'Center')
        self.layer = p.GetString("draw_strip_layer","A")
        self.draw_strip_ui = self.taskbox()
        selections = Gui.Selection.getSelection()
        if selections:
            wire = selections[0]
            if hasattr(wire, 'Proxy') and hasattr(wire.Proxy, 'Type')  and wire.Proxy.Type == 'Wire':
                self.node = wire.Points
                FreeCAD.ActiveDocument.removeObject(wire.Name)
                wire = Part.makePolygon(self.node)
                shape = osafe_funcs.get_left_right_offset_wire_and_shape(wire, self.strip_left_width, self.strip_right_width)[0]
                self.obj.Shape = Part.makeCompound([wire, shape])
        self.ui.layout.insertWidget(0, self.draw_strip_ui)
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
        if len(self.node) > 1:
            self.node.pop()
            # self.linetrack.update(self.node)
            wire = Part.makePolygon(self.node)
            shape = osafe_funcs.get_left_right_offset_wire_and_shape(wire, self.strip_left_width, self.strip_right_width)[0]
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
            shape = osafe_funcs.get_left_right_offset_wire_and_shape(wire, self.strip_left_width, self.strip_right_width)[0]
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
        # if self.ui:
            # self.linetrack.finalize()
        if not utils.getParam("UiMode", 1):
            Gui.Control.closeDialog()
        if self.obj:
            # Remove temporary object, if any
            old = self.obj.Name
            todo.ToDo.delay(self.doc.removeObject, old)
        if len(self.node) > 1:
            # The command to run is built as a series of text strings
            # to be committed through the `draftutils.todo.ToDo` class.
            try:
                FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Draw Strip"))
                wire = Draft.make_wire(self.node)
                make_strip(wire, self.layer, "column", self.strip_width, self.strip_left_width, self.strip_right_width, self.strip_align)
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
        Gui.Selection.clearSelection()
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
        punch_path = Path(__file__).parent.parent
        w = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'draw_strip.ui'))
    
        self.layer_box = w.strip_layer
        self.width_spinbox = w.width_spinbox
        self.left_width_spinbox = w.left_width_spinbox
        self.right_width_spinbox = w.right_width_spinbox
        self.align_box = w.align
        # self.layer_box.setValue(self.bx / 10))
        self.width_spinbox.setValue(int(self.strip_width / 10))
        self.left_width_spinbox.setValue(int(self.strip_left_width / 10))
        self.right_width_spinbox.setValue(int(self.strip_right_width / 10))
        i = self.align_box.findText(self.strip_align)
        self.align_box.setCurrentIndex(i)
        i = self.layer_box.findText(self.layer)
        self.layer_box.setCurrentIndex(i)

        # connect slots
        self.width_spinbox.valueChanged.connect(self.set_width)
        self.left_width_spinbox.valueChanged.connect(self.set_width)
        self.right_width_spinbox.valueChanged.connect(self.set_width)
        self.align_box.currentIndexChanged.connect(self.set_width)
        self.align_box.currentIndexChanged.connect(self.update_gui)
        self.layer_box.currentIndexChanged.connect(self.set_layer)
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
        self.strip_width = self.width_spinbox.value() * 10
        align = self.align_box.currentText()
        if align == 'Left':
            sl = self.left_width_spinbox.value() * 10
            sr = self.strip_width - sl
        elif align == 'Right':
            sr = self.right_width_spinbox.value() * 10
            sl = self.strip_width - sr
        elif align == 'Center':
            sr = sl = self.strip_width / 2
        self.left_width_spinbox.setValue(int(sl / 10))
        self.right_width_spinbox.setValue(int(sr / 10))
        self.strip_left_width = sl
        self.strip_right_width = sr
        self.strip_align = align
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        p.SetFloat("draw_strip_width",self.strip_width)
        p.SetFloat("draw_strip_left_width",self.strip_left_width)
        p.SetFloat("draw_strip_right_width",self.strip_right_width)
        p.SetString("draw_strip_align",self.strip_align)
        self.drawUpdate(self.point)

    def set_layer(self):
        self.layer = self.draw_strip_ui.strip_layer.currentText()
        if self.layer in  ('A', 'B'):
            layer = self.layer.lower()
            osafe_funcs.format_view_object(
                obj=self.obj,
                shape_color_entity=f'design_layer_{layer}_shape_color',
                line_width_entity='design_layer_a_line_width',
                display_mode_entity='design_layer_a_display_mode',
                line_color_entity=f'design_layer_{layer}_line_color',
                transparency_entity='design_layer_a_transparency',
            )
        elif self.layer == 'other':
            self.obj.ViewObject.ShapeColor = (0.20,1.00,0.00)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetString("draw_strip_layer",self.layer)





Gui.addCommand('osafe_draw_strip', DrawStrip())

## @}
