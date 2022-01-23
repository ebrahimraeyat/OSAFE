from pathlib import Path

from PySide2.QtWidgets import QMessageBox

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

    def draw(self):
        draw_x = self.form.x_strips.isChecked()
        draw_y = self.form.y_strips.isChecked()
        x_width = self.form.x_width.value()
        y_width = self.form.y_width.value()
        x_layer_name = self.form.x_layer_name.currentText()
        y_layer_name = self.form.y_layer_name.currentText()
        equal = self.form.equal.isChecked()
        from safe.punch import punch_funcs
        punch_funcs.draw_strip_automatically_in_mat_foundation(
            # foundation=self.foundation,
            x_width=x_width * 10,
            y_width=y_width * 10,
            x_layer_name=x_layer_name,
            y_layer_name=y_layer_name,
            draw_x=draw_x,
            draw_y=draw_y,
            equal=equal,
        )
    
    def accept(self):
        Gui.Control.closeDialog()
