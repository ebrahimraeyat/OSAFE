from pathlib import Path

from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QMessageBox, QFileDialog

civiltools_path = Path(__file__).absolute().parent.parent


class Form(*loadUiType(str(civiltools_path / 'widgets' / 'weakness.ui'))):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.setupUi(self)
        self.form = self
        self.etabs = etabs_obj
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.set_filenames()
        self.create_connections()

    def accept(self):
        from civilTools import table_model
        if not self.etabs.success:
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
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
        table_model.show_results(data, headers, table_model.ColumnsRatioModel)
        table_model.show_results(data2, headers2, table_model.BeamsRebarsModel)

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

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
        beam_name = item.text()
        self.etabs.view.show_frame(beam_name)


    def get_filename(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'select *.EDB file',
                                                  self.directory, "ETBAS Model(*.EDB)")
        if filename == '':
            return
        self.weakness_file.setText(filename)

