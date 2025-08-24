from pathlib import Path


import numpy as np

from PySide import QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP, Qt
from PySide.QtGui import QTableWidgetItem, QMessageBox

import FreeCAD
import Part
from FreeCAD import Vector
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
from osafe_objects.base_foundation import make_base_foundation


class BaseFoundation(gui_lines.Line):
    """Gui command for the Base Foundation tool."""

    def __init__(self):
        super(BaseFoundation, self).__init__(wiremode=True)

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "osafe_base_foundation",
            "Base Foundation")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "osafe_base_foundation",
            "Draw Base Foundation")
        path = str(
                   Path(__file__).parent.parent / "osafe_images" / "base_foundation.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}
    
    def Activated(self):
        """
        Execute when the command is called.
        """
        super(BaseFoundation, self).Activated(name=translate("OSAFE", "BaseFoundation"))
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
            if hasattr(wire, 'Proxy') and hasattr(wire.Proxy, 'Type')  and wire.Proxy.Type == 'Wire':
                self.node = wire.Points
                FreeCAD.ActiveDocument.removeObject(wire.Name)
                wire = Part.makePolygon(self.node)
                shape = osafe_funcs.get_left_right_offset_wire_and_shape(wire, self.bf_left_width, self.bf_right_width)[0]
                self.obj.Shape = Part.makeCompound([wire, shape])
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
        if len(self.node) > 1:
            self.node.pop()
            # self.linetrack.update(self.node)
            wire = Part.makePolygon(self.node)
            shape = osafe_funcs.get_left_right_offset_wire_and_shape(wire, self.bf_left_width, self.bf_right_width)[0]
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
            shape = osafe_funcs.get_left_right_offset_wire_and_shape(wire, self.bf_left_width, self.bf_right_width)[0]
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
        soil_modulus = self.get_ks()
        p.SetFloat("foundation_fc",fc)
        p.SetFloat("base_foundation_soil_modulus", self.soil_modulus_spin.value())
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
                FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Base Foundation"))
                wire = Draft.make_wire(self.node)
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
        w = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'base_foundation.ui'))
    
        self.layer_box = w.strip_layer
        self.width_spinbox = w.width_spinbox
        self.left_width_spinbox = w.left_width_spinbox
        self.right_width_spinbox = w.right_width_spinbox
        self.height_spinbox = w.height_spinbox
        self.align_box = w.align
        self.soil_modulus_spin = w.soil_modulus
        self.fc_spin = w.fc
        self.ks_input_group = w.ks_input_group
        self.add_ks_row_button = w.add_ks_row_button
        self.remove_ks_row_button = w.remove_ks_row_button
        self.ks_table = w.ks_table
        self.ks_label = w.ks_label
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
        self.create_connections()
        return w
    
    def create_connections(self):
        self.width_spinbox.valueChanged.connect(self.set_width)
        self.left_width_spinbox.valueChanged.connect(self.set_width)
        self.right_width_spinbox.valueChanged.connect(self.set_width)
        self.height_spinbox.valueChanged.connect(self.set_height)
        self.align_box.currentIndexChanged.connect(self.set_width)
        self.align_box.currentIndexChanged.connect(self.update_gui)
        self.layer_box.currentIndexChanged.connect(self.set_layer)
        self.ks_input_group.clicked.connect(self.ks_input_group_clicked)
        self.add_ks_row_button.clicked.connect(self.add_ks_row)
        self.remove_ks_row_button.clicked.connect(self.remove_ks_row)

    def add_ks_row(self):
        row_count = self.ks_table.rowCount()
        self.ks_table.insertRow(row_count)
        for i in (0, 1):
            item = QTableWidgetItem(f"{i + 1}")
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.ks_table.setItem(row_count, i, item)

    def remove_ks_row(self):
        selected_row = self.ks_table.currentRow()
        if selected_row >= 0:
            self.ks_table.removeRow(selected_row)

    def ks_input_group_clicked(self, checked: bool):
        self.soil_modulus_spin.setEnabled(not checked)
        self.ks_label.setEnabled(not checked)

    def get_ks(self):
        if self.ks_input_group.isChecked():
            """Retrieves all data from a QTableWidget."""
            data = []
            for row in range(self.ks_table.rowCount()):
                row_data = []
                for col in range(self.ks_table.columnCount()):
                    item = self.ks_table.item(row, col)
                    row_data.append(float(item.text()))
                data.append(row_data)
            data = sorted(data, key=lambda x: x[0])
            if len(data) < 2:
                QMessageBox.warning(None, "Ks", "Please Enter at least two values for Ks.")
                return None
            widths, kss = zip(*data)
            m, c = np.polyfit(widths, kss, 1)
            ks = f"{m:.3f} * .width.Value / 1000 + {c:.3f}"
        else:
            ks = str(self.soil_modulus_spin.value())
        return ks

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
        self.layer = self.base_foundation_ui.strip_layer.currentText()
        if self.layer in  ('A', 'B'):
            layer = self.layer.lower()
            osafe_funcs.format_view_object(
                obj=self.obj,
                shape_color_entity=f'base_foundation_{layer}_shape_color',
                line_width_entity='base_foundation_a_line_width',
                display_mode_entity='base_foundation_a_display_mode',
                line_color_entity=f'base_foundation_{layer}_line_color',
                transparency_entity='base_foundation_a_transparency',
            )
        elif self.layer == 'other':
            self.obj.ViewObject.ShapeColor = (0.20,1.00,0.00)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetString("base_foundation_layer",self.layer)





Gui.addCommand('osafe_base_foundation', BaseFoundation())

## @}
