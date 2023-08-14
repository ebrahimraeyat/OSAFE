from pathlib import Path


import FreeCAD
import FreeCADGui as Gui

from PySide2.QtWidgets import QMessageBox

from safe.punch.py_widget import resource_rc

punch_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(
        self,
        ):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'export_strips_panel.ui'))
        self.etabs_clicked = False
        self.create_connections()

    def fill_levels(self):
        if not self.etabs_clicked:
            import find_etabs
            etabs, filename = find_etabs.find_etabs(backup=True)
            if (
                etabs is None or
                filename is None
                ):
                return
            levels_names = self.etabs.story.get_level_names()
            self.form.levels_list.addItems(levels_names[1:])
            self.etabs_clicked = True

    def set_filename(self):
        filename = Path(self.etabs.get_filename_path_with_suffix('.F2k'))
        self.form.filename.setText(str(filename))
        
    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.export_strips.clicked.connect(self.export_strips)
        self.form.help.clicked.connect(self.show_help)
        self.form.cancel_pushbutton.clicked.connect(self.accept)
        self.form.safe20.clicked.connect(self.selection_changed)
        self.form.safe16.clicked.connect(self.selection_changed)
        self.form.etabs.clicked.connect(self.selection_changed)
        self.form.etabs.clicked.connect(self.fill_levels)

    def selection_changed(self):
        if self.form.safe20.isChecked():
            self.form.levels_list.setEnabled(False)
            self.form.filename.setEnabled(False)
            self.form.browse.setEnabled(False)
        elif self.form.safe16.isChecked():
            self.form.levels_list.setEnabled(False)
            self.form.filename.setEnabled(True)
            self.form.browse.setEnabled(True)
        elif self.form.etabs.isChecked():
            self.form.levels_list.setEnabled(True)
            self.form.filename.setEnabled(False)
            self.form.browse.setEnabled(False)

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

    def export_strips(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            QMessageBox.warning(None, "Open FreeCAD Model", "Can not find any ActiveDocument in FreeCAD!")
            return
        if self.form.etabs.isChecked():
            story = self.form.levels_list.currentText()
            self.etabs.area.export_freecad_strips(
                doc=doc,
                story=story,
                )
            self.etabs.view.refresh_view()
        elif self.form.safe20.isChecked():
            import find_etabs
            etabs, filename = find_etabs.find_etabs(software='SAFE', backup=False)
            if (
                etabs is None or
                filename is None
                ):
                return
            etabs.area.export_freecad_strips(doc=doc)
            etabs.view.refresh_view()
        elif self.form.safe16.isChecked():
            raise NotImplementedError
        QMessageBox.information(None, "Applied to Software", "Strips Written Successfully.")
    
    def show_help(self):
        from freecad_funcs import show_help
        show_help('import_model.html', 'OSAFE')

    def getStandardButtons(self):
        return 0

    def accept(self):
        Gui.Control.closeDialog()
