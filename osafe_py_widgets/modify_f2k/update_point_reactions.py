from pathlib import Path

# from PySide import QtGui
# from PySide.QtGui import QFileDialog
from PySide.QtGui import QMessageBox

import FreeCAD
# import FreeCADGui as Gui

import create_f2k


osafe_path = Path(__file__).absolute().parent.parent.parent


class Form(): # QtGui.QWidget):
    def __init__(self, etabs_model, filename):
        # super(Form, self).__init__()
        # self.form = Gui.PySideUic.loadUi(str(osafe_path / 'widgets' / 'define' / 'load_combinations_to_f2k.ui'))
        self.etabs = etabs_model
        self.filename = filename
        # filename = Path(self.etabs.SapModel.GetModelFilename()).with_suffix('.F2k')
        # self.form.filename.setText(str(filename))
        # self.create_connections()
    
    def update_point_loads(self):
        safe = create_f2k.ModifyF2kFile(
        input_f2k=self.filename,
        etabs=self.etabs,
        load_cases=[],
        case_types=[],
        model_datum=0,
        )
        safe.add_point_loads()
        safe.write()
        QMessageBox.information(None, 'Successfull',f'Successfully update point loads in {self.filename}.')

            
    # def create_connections(self):
    #     self.form.add_to_f2k_button.clicked.connect(self.update_point_loads)
    #     self.form.browse.clicked.connect(self.browse)

    # def reject(self):
    #     Gui.Control.closeDialog()

    # def browse(self):
    #     ext = '.f2k'
    #     filters = f"{ext[1:]} (*{ext})"
    #     filename, _ = QFileDialog.getOpenFileName(None, 'select file',
    #                                             None, filters)
    #     if not filename:
    #         return
    #     if not filename.lower().endswith(ext):
    #         filename += ext
    #     self.form.filename.setText(filename)
    