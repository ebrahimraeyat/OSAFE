from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

from safe.punch.py_widget import resource_rc
from PySide2.QtGui import QPixmap

punch_path = Path(__file__).parent.parent
import etabs_obj


class EtabsTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'etabs_panel.ui'))
        self.etabs = etabs_obj.EtabsModel(backup=False)
        self.set_foundation_level()
        self.set_story()
        self.set_filename()
        self.create_connections()

    def set_filename(self):
        filename = Path(self.etabs.SapModel.GetModelFilename()).with_suffix('.F2k')
        self.form.filename.setText(str(filename))
        

    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)

    def set_foundation_level(self):
        self.etabs.set_current_unit('N', 'm')
        base_level = self.etabs.story.get_base_name_and_level()[1]
        self.form.foundation_level.setValue(base_level)

    def set_story(self):
        stories = self.etabs.SapModel.Story.GetNameList()[1]
        self.form.story.addItems(stories)
        self.form.story.setCurrentIndex(len(stories) - 1)

    def browse(self):
        ext = '.f2k'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)

    def accept(self):
        if self.form.beams_group.isChecked():
            self.import_beams_columns()
        if self.form.f2k_groupbox.isChecked():
            self.create_f2k()
        Gui.Control.closeDialog()

    def import_beams_columns(self):
        from safe.punch import etabs_punch
        foundation_level = self.form.foundation_level.value() * 1000
        story = self.form.story.currentText()
        selected_beams = self.form.selected_beams.isChecked()
        exclude_selected_beams = self.form.exclude_selected_beams.isChecked()
        beams_names = None
        conc_beams, _  = self.etabs.frame_obj.get_beams_columns(story=story)
        steel_beams, _  = self.etabs.frame_obj.get_beams_columns(story=story, type_=1)
        beams = steel_beams + conc_beams
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
                etabs_model = self.etabs,
                beam_names = beams_names,
                top_of_foundation=foundation_level,
            )
        punch.import_data()

    def create_f2k(self):
        filename = self.form.filename.text()
        filename_path = Path(filename)
        name = f"{filename_path.name.rstrip(filename_path.suffix)}_export{filename_path.suffix}"
        output_filename = str(filename_path.with_name(name))
        import create_f2k
        from safe.punch.f2k_object import make_safe_f2k
        make_safe_f2k(filename, output_filename)
        writer = create_f2k.CreateF2kFile(filename_path, self.etabs)
        pixmap = QPixmap(str(punch_path / 'Resources' / 'icons' / 'tick.svg'))
        d = {
            1 : self.form.one,
            2 : self.form.two,
            3 : self.form.three,
            4 : self.form.four,
            5 : self.form.five,
        }
        for ret in writer.create_f2k():
            if type(ret) == tuple and len(ret) == 3:
                message, percent, number = ret
                if type(message) == str and type(percent) == int:
                    self.form.result_label.setText(message)
                    self.form.progressbar.setValue(percent)
                    if number < 6:
                        d[number].setPixmap(pixmap)
            elif type(ret) == bool:
                if not ret:
                    self.form.result_label.setText("Error Occurred, process did not finished.")
                self.form.start_button.setEnabled(False)
            elif type(ret) == str:
                self.form.result_label.setText(ret)
 
if __name__ == '__main__':
    panel = EtabsTaskPanel()
