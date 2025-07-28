from pathlib import Path

import numpy as np


import FreeCAD
import FreeCADGui as Gui
from draftutils.translate import translate

from PySide2.QtWidgets import QMessageBox, QTableWidgetItem
from PySide2.QtCore import Qt

from osafe_funcs import osafe_funcs
from osafe_py_widgets import resource_rc

punch_path = Path(__file__).parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'base_foundation_panel.ui'))
        self.create_connections()


    def getStandardButtons(self):
        return 0

    def create_connections(self):
        self.form.create_pushbutton.clicked.connect(self.create)
        self.form.cancel_pushbutton.clicked.connect(self.accept)
        self.form.ks_input_group.clicked.connect(self.ks_input_group_clicked)
        self.form.add_ks_row_button.clicked.connect(self.add_ks_row)
        self.form.remove_ks_row_button.clicked.connect(self.remove_ks_row)

    def add_ks_row(self):
        row_count = self.form.ks_table.rowCount()
        self.form.ks_table.insertRow(row_count)
        for i in (0, 1):
            item = QTableWidgetItem(f"{i + 1}")
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.form.ks_table.setItem(row_count, i, item)

    def remove_ks_row(self):
        selected_row = self.form.ks_table.currentRow()
        if selected_row >= 0:
            self.form.ks_table.removeRow(selected_row)

    def ks_input_group_clicked(self, checked: bool):
        self.form.soil_modulus.setEnabled(not checked)
        self.form.ks_label.setEnabled(not checked)

    def create(self):
        x_stirp_name = self.form.x_strip_name.currentText()
        y_stirp_name = self.form.y_strip_name.currentText()
        width = self.form.width_spinbox.value() * 10
        height = self.form.height_spinbox.value() * 10
        soil_modulus = self.get_ks()
        angle = self.form.angle_spinbox.value()
        selection = self.form.selection_checkbox.isChecked()
        doc = FreeCAD.ActiveDocument
        beams = []
        sel = []
        if selection:
            sel = Gui.Selection.getSelection()
            for o in sel:
                if (
                    hasattr(o, "type") and
                    o.type == 'Beam'
                    ):
                    beams.append(o)
        else:
            for o in doc.Objects:
                if (
                    hasattr(o, "type") and
                    o.type == 'Beam'
                    ):
                    beams.append(o)

        if len(beams) == 0:
            if len(sel) > 0:
                message = "There is No Beams in selected objects."
            else:
                message = "There is No Beams in Model."
            QMessageBox.warning(None, "Beams", message)
            return
        if len(sel) == 0: # Check for beams that now are in base foundations
            used_beam = osafe_funcs.get_beams_in_doc_that_belogns_to_base_foundations(doc)
            current_beam = [beam.Name for beam in beams]
            new_beams = set(current_beam).difference(used_beam)
            if len(new_beams) == 0:
                message = "There is No Remained Beams in Model."
                QMessageBox.warning(None, "Beams", message)
                return
            beams = [doc.getObjectsByLabel(name)[0] for name in new_beams]
        FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Base Foundations"))
        osafe_funcs.make_automatic_base_foundation(beams, width, x_stirp_name, y_stirp_name, angle, height, soil_modulus)
        FreeCAD.ActiveDocument.commitTransaction()
        Gui.Selection.clearSelection()
        Gui.Control.closeDialog()

    def accept(self):
        Gui.Control.closeDialog()
        
    def get_ks(self):
        if self.form.ks_input_group.isChecked():
            """Retrieves all data from a QTableWidget."""
            data = []
            for row in range(self.form.ks_table.rowCount()):
                row_data = []
                for col in range(self.form.ks_table.columnCount()):
                    item = self.form.ks_table.item(row, col)
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
            ks = str(self.form.soil_modulus.value())
        return ks