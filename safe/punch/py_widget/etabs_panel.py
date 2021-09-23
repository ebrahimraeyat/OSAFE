import sys
import FreeCAD
import FreeCADGui as Gui

# from PySide2.QtCore import *
# from PySide2.QtGui import *
# from PySide2.QtWidgets import *
from safe.punch import geom
from pathlib import Path
# from safe.punch.colorbar import ColorMap
punch_path = Path(__file__).parent.parent


class EtabsTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'etabs_panel.ui'))
        self.create_connections()

    def create_connections(self):
        self.form.import_button.clicked.connect(self.import_from_etabs)
        self.form.mat.clicked.connect(self.update_ui)
        self.form.tape.clicked.connect(self.update_ui)

    def update_ui(self):
        if self.form.mat.isChecked():
            self.form.beams_group.setEnabled(False)
            self.form.width_label.setEnabled(False)
            self.form.width_spinbox.setEnabled(False)
        elif self.form.tape.isChecked():
            self.form.beams_group.setEnabled(True)
            self.form.width_label.setEnabled(True)
            self.form.width_spinbox.setEnabled(True)

    def import_from_etabs(self):
        # sys.path.insert(0, str(punch_path))
        from safe.punch import etabs_punch
        cover = self.form.cover.value() * 10
        fc = self.form.fc.value()
        height = self.form.height_spinbox.value() * 10
        width = self.form.width_spinbox.value() * 10
        etabs = etabs_punch.EtabsPunch(
                cover = cover,
                fc = fc,
                height = height,
                width = width,
            )
        name = etabs.etabs.get_file_name_without_suffix()
        FreeCAD.newDocument(name)
        etabs.create_foundation()
        etabs.create_punches()


if __name__ == '__main__':
    panel = EtabsTaskPanel()
