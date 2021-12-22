from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox

cfactor_path = Path(__file__).absolute().parent.parent

weakness_base, weakness_window = uic.loadUiType(cfactor_path / 'widgets' / 'show_weakness.ui')

class WeaknessForm(weakness_base, weakness_window):
    def __init__(self, etabs_model, tabel_model, parent=None):
        super(WeaknessForm, self).__init__(parent)
        self.setupUi(self)
        self.etabs = etabs_model
        self.table_model = tabel_model
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.set_filenames()
        self.create_connections()

    def accept(self):
        use_json_file = self.file_groupbox.isChecked()
        dir_ = 'x' if self.x_radio_button.isChecked() else 'y'
        if use_json_file:
            json_file = Path(self.json_file.text())
        else:
            json_file = Path(self.etabs.SapModel.GetModelFilepath()) / f'columns_pmm_beams_rebars_{dir_}.json'
        if json_file.exists():
            ret = self.etabs.load_from_json(json_file)
            data, headers, data2, headers2 = ret
            self.table_model.show_results(data, headers, self.table_model.ColumnsRatioModel)
            self.table_model.show_results(data2, headers2, self.table_model.BeamsRebarsModel)
        else:
            err = "Please first get weakness ration, then show it!"
            QMessageBox.critical(self, "Error", str(err))
            return None

    def set_filenames(self):
        f = Path(self.etabs.SapModel.GetModelFilename())
        if self.x_radio_button.isChecked():
            self.json_file.setText(str(f.with_name('columns_pmm_beams_rebars_x.json')))
        elif self.y_radio_button.isChecked():
            self.json_file.setText(str(f.with_name('columns_pmm_beams_rebars_y.json')))
        
    def create_connections(self):
        self.weakness_button.clicked.connect(self.get_filename)
        self.x_radio_button.toggled.connect(self.set_filenames)
        self.y_radio_button.toggled.connect(self.set_filenames)
        self.file_groupbox.toggled.connect(self.change_frame_enable)

    def change_frame_enable(self):
        if self.file_groupbox.isChecked():
            self.dir_frame.setEnabled(False)
        else:
            self.dir_frame.setEnabled(True)

    def get_filename(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'select *.json file',
                                                  self.directory, "Results(*.json)")
        if filename == '':
            return
        self.json_file.setText(filename)

