from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent
from etabs_api import etabs_obj


class SafeTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'safe_panel.ui'))
        self.create_connections()

    def create_connections(self):
        self.form.export_button.clicked.connect(self.export_to_safe)

    def export_to_safe(self):
        software = self.form.software.currentText()
        etabs = etabs_obj.EtabsModel(backup=False, software=software)
        etabs.unlock_model()
        doc = FreeCAD.ActiveDocument
        if self.form.slabs_checkbox.isChecked():
            soil_name = self.form.soil_name.text()
            soil_modulus = self.form.soil_modulus.value()
            etabs.area.export_freecad_slabs(
                doc,
                soil_name=soil_name,
                soil_modulus=soil_modulus,
            )
        if self.form.openings_checkbox.isChecked():
            etabs.area.export_freecad_openings(doc)
        if self.form.strips_checkbox.isChecked():
            if doc.Foundation.foundation_type == 'Strip':
                etabs.area.export_freecad_strips(doc)
        if self.form.stiff_elements_checkbox.isChecked():
            etabs.area.export_freecad_stiff_elements(doc)
        etabs.SapModel.View.RefreshView()


if __name__ == '__main__':
    panel = SafeTaskPanel()