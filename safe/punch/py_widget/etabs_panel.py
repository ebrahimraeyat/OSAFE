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
from etabs_api import etabs_obj


class EtabsTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'etabs_panel.ui'))
        self.etabs = etabs_obj.EtabsModel(backup=False)
        self.set_story()
        self.create_connections()

    def create_connections(self):
        self.form.import_button.clicked.connect(self.import_from_etabs)
        self.form.mat.clicked.connect(self.update_ui)
        self.form.tape.clicked.connect(self.update_ui)

    def set_story(self):
        stories = self.etabs.SapModel.Story.GetNameList()[1]
        self.form.story.addItems(stories)
        self.form.story.setCurrentIndex(len(stories) - 1)

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
        story = self.form.story.currentText()
        selected_beams = self.form.selected_beams.isChecked()
        exclude_selected_beams = self.form.exclude_selected_beams.isChecked()
        beams_names = None
        beams, _  = self.etabs.frame_obj.get_beams_columns(story=story)
        if (selected_beams or exclude_selected_beams):
            names = self.etabs.select_obj.get_selected_obj_type(2)
            names = [name for name in names if self.etabs.frame_obj.is_beam(name)]
            if selected_beams:
                beams_names = set(names).intersection(beams)
            elif exclude_selected_beams:
                beams_names = set(beams).difference(names)
        elif self.form.all_beams.isChecked():
            beams_names = beams
        punch = etabs_punch.EtabsPunch(
                cover = cover,
                fc = fc,
                height = height,
                width = width,
                etabs_model = self.etabs,
                beam_names = beams_names
            )
        punch.import_data()


if __name__ == '__main__':
    panel = EtabsTaskPanel()
