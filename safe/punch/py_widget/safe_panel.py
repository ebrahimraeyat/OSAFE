from pathlib import Path

import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent
from etabs_api import etabs_obj


class SafeTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'safe_panel.ui'))
        self.etabs = etabs_obj.EtabsModel(backup=False, software='SAFE')
        self.create_connections()

    def create_connections(self):
        self.form.export_button.clicked.connect(self.export_to_safe)

    def export_to_safe(self):
        if self.form.slabs_checkbox.isChecked():
            self.etabs.area.export_freecad_slabs()
        if self.form.openings_checkbox.isChecked():
            self.etabs.area.export_freecad_openings()
        self.etabs.SapModel.View.RefreshView()


if __name__ == '__main__':
    panel = SafeTaskPanel()
