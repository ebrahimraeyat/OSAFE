from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

from safe.punch.py_widget import resource_rc
from PySide2.QtGui import QPixmap

punch_path = Path(__file__).parent.parent


class Form:
    def __init__(self, etabs, parent=None):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'create_f2k.ui'))
        self.etabs = etabs
        filename = Path(self.etabs.SapModel.GetModelFilename()).with_suffix('.F2k')
        self.form.filename.setText(str(filename))
        self.create_connections()

    def create_connections(self):
        self.form.start_button.clicked.connect(self.accept)
        self.form.browse.clicked.connect(self.browse)
        self.form.close_button.clicked.connect(self.reject)

    def reject(self):
        Gui.Control.closeDialog()

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
        filename = self.form.filename.text()
        import create_f2k
        writer = create_f2k.CreateF2kFile(Path(filename), self.etabs)
        
        if FreeCAD.ActiveDocument:
            foun = FreeCAD.ActiveDocument.Foundation
            if foun:
                foun.F2K = filename
        
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

