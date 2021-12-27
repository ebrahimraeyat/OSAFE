from pathlib import Path

from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QFileDialog, QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent


class Form(*loadUiType(str(civiltools_path / 'widgets' / 'show_weakness.ui'))):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.setupUi(self)
        self.form = self
        self.etabs = etabs_obj
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
            from civilTools import table_model
            ret = self.etabs.load_from_json(json_file)
            data, headers, data2, headers2 = ret
            table_model.show_results(data, headers, table_model.ColumnsRatioModel)
            table_model.show_results(data2, headers2, table_model.BeamsRebarsModel)
        else:
            err = "Please first get weakness ration, then show it!"
            QMessageBox.critical(self, "Error", str(err))
            return None

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

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

