from pathlib import Path

from PySide2.QtWidgets import QMessageBox
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui as Gui

from safe.punch.py_widget import resource_rc

punch_path = Path(__file__).parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'draw_automatic_strip.ui'))
        self.create_connections()

    def create_connections(self):
        self.form.draw_button.clicked.connect(self.draw)
        self.form.mat_foundation.clicked.connect(self.uncheck_strip)
        self.form.strip_foundation.clicked.connect(self.uncheck_mat)
        self.form.help.clicked.connect(self.show_help)

    def uncheck_strip(self, state):
        # if state == Qt.Checked:
        self.form.mat_foundation.setChecked(True)
        self.form.strip_foundation.setChecked(False)
    
    def uncheck_mat(self, state):
        self.form.mat_foundation.setChecked(False)
        self.form.strip_foundation.setChecked(True)

    def draw(self):
        doc = FreeCAD.ActiveDocument
        strips = []
        for obj in doc.Objects:
            if (
                isinstance(obj, FreeCAD.DocumentObjectGroup) and
                'strips' in obj.Label
            ):
                strips.append(obj)
        if strips and QMessageBox.question(
            None,
            'Remove Strips',
            'There is ' + ' and '.join([s.Label for s in strips]) + ' exists in Model, Do you want to remove those?',
            ) == QMessageBox.Yes:
            for strip in strips:
                for o in strip.Group:
                    FreeCAD.ActiveDocument.removeObject(o.Base.Name)
                    FreeCAD.ActiveDocument.removeObject(o.Name)
                FreeCAD.ActiveDocument.removeObject(strip.Name)

        from safe.punch import punch_funcs
        if self.form.mat_foundation.isChecked():
            draw_x = self.form.x_strips.isChecked()
            draw_y = self.form.y_strips.isChecked()
            x_width = self.form.x_width.value()
            y_width = self.form.y_width.value()
            x_layer_name = self.form.x_layer_name.currentText()
            y_layer_name = self.form.y_layer_name.currentText()
            equal = self.form.equal.isChecked()
            consider_openings = self.form.consider_openings.isChecked()
            punch_funcs.draw_strip_automatically_in_mat_foundation(
                # foundation=self.foundation,
                x_width=x_width * 10,
                y_width=y_width * 10,
                x_layer_name=x_layer_name,
                y_layer_name=y_layer_name,
                draw_x=draw_x,
                draw_y=draw_y,
                equal=equal,
                consider_openings=consider_openings,
            )
        else:
            punch_funcs.draw_strip_automatically_in_strip_foundation()
        self.accept()
        Gui.Selection.clearSelection()

    def show_help(self):
        from help.show_help import show
        show('make_auto_strip.html')
    
    def accept(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return int(QtWidgets.QDialogButtonBox.Cancel)
