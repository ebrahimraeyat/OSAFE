from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

from PySide2.QtWidgets import QMessageBox

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

    def create(self):
        north_dist = self.form.north_distance.value() * 10 if self.form.north_checkbox.isChecked() else None
        south_dist = self.form.south_distance.value() * 10 if self.form.south_checkbox.isChecked() else None
        east_dist = self.form.east_distance.value() * 10 if self.form.east_checkbox.isChecked() else None
        west_dist = self.form.west_distance.value() * 10 if self.form.west_checkbox.isChecked() else None
        x_stirp_name = self.form.x_strip_name.currentText()
        y_stirp_name = self.form.y_strip_name.currentText()
        width = self.form.width_spinbox.value() * 10
        height = self.form.height_spinbox.value() * 10
        soil_modulus = self.form.soil_modulus.value()
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
        osafe_funcs.make_automatic_base_foundation(beams, width, north_dist, south_dist,
                east_dist, west_dist, x_stirp_name, y_stirp_name, angle, height, soil_modulus)
        Gui.Selection.clearSelection()
        Gui.Control.closeDialog()

    def accept(self):
        Gui.Control.closeDialog()
