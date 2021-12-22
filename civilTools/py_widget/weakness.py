from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox

cfactor_path = Path(__file__).absolute().parent.parent

weakness_base, weakness_window = uic.loadUiType(cfactor_path / 'widgets' / 'weakness.ui')

class WeaknessForm(weakness_base, weakness_window):
    def __init__(self, etabs_model, table_model, parent=None):
        super(WeaknessForm, self).__init__(parent)
        self.setupUi(self)
        self.etabs = etabs_model
        self.table_model = table_model
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.set_filenames()
        self.create_connections()

    def accept(self):
        use_weakness_file = self.file_groupbox.isChecked()
        dir_ = 'x' if self.x_radio_button.isChecked() else 'y'
        if use_weakness_file:
            weakness_filepath = Path(self.weakness_file.text())
            if weakness_filepath.exists():
                ret = self.etabs.frame_obj.get_beams_columns_weakness_structure(weakness_filename=weakness_filepath, dir_=dir_)
        else:
            ret = self.etabs.frame_obj.get_beams_columns_weakness_structure(dir_=dir_)
        if not ret:
            err = "Please select one beam in ETABS model!"
            QMessageBox.critical(self, "Error", str(err))
            return None
        data, headers, data2, headers2 = ret
        self.table_model.show_results(data, headers, self.table_model.ColumnsRatioModel)
        self.table_model.show_results(data2, headers2, self.table_model.BeamsRebarsModel)
        super(WeaknessForm, self).accept()

    def fill_selected_beams(self):
        self.beams_list.clear()
        try:
            selected = self.etabs.SapModel.SelectObj.GetSelected()
        except IndexError:
            return
        types = selected[1]
        names = selected[2]
        beams = []
        for type, name in zip(types, names):
            if type == 2 and self.etabs.SapModel.FrameObj.GetDesignOrientation(name)[0] == 2:
                beams.append(name)
        if len(beams) > 0:
            self.beams_list.addItems(beams)
            self.beams_list.setCurrentRow(len(beams) - 1)

    def set_filenames(self):
        f = Path(self.etabs.SapModel.GetModelFilename())
        if self.x_radio_button.isChecked():
            self.weakness_file.setText(str(f.with_name('weakness_x.EDB')))
        elif self.y_radio_button.isChecked():
            self.weakness_file.setText(str(f.with_name('weakness_y.EDB')))
        
    def create_connections(self):
        self.weakness_button.clicked.connect(self.get_filename)
        self.beams_list.itemClicked.connect(self.beam_changed)
        self.refresh_button.clicked.connect(self.fill_selected_beams)
        self.x_radio_button.toggled.connect(self.set_filenames)
        self.y_radio_button.toggled.connect(self.set_filenames)

    def beam_changed(self, item):
        # item = self.beams_list.currentItem()
        beam_name = item.text()
        self.etabs.view.show_frame(beam_name)


    def get_filename(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'select *.EDB file',
                                                  self.directory, "ETBAS Model(*.EDB)")
        if filename == '':
            return
        self.weakness_file.setText(filename)

