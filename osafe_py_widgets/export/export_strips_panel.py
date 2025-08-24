from pathlib import Path


import FreeCAD
import FreeCADGui as Gui

from PySide.QtGui import QMessageBox

from osafe_py_widgets import resource_rc

punch_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(
        self,
        ):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'export_strips_panel.ui'))
        self.etabs_clicked = False
        self.etabs = None
        self.create_connections()

    def fill_levels(self):
        if not self.etabs_clicked:
            import find_etabs
            self.etabs, filename = find_etabs.find_etabs(backup=True)
            if (
                self.etabs is None or
                filename is None
                ):
                return
            levels_names = self.etabs.story.get_level_names()
            self.form.levels_list.addItems(levels_names[1:])
            self.etabs_clicked = True

    def set_filename(self):
        filename = Path(self.etabs.get_filename_path_with_suffix('.F2k'))
        self.form.f2k_filename.setText(str(filename))
        
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
            self.form.f2k_filename.setEnabled(False)
            self.form.browse.setEnabled(False)
        elif self.form.safe16.isChecked():
            self.form.levels_list.setEnabled(False)
            self.form.f2k_filename.setEnabled(True)
            self.form.browse.setEnabled(True)
        elif self.form.etabs.isChecked():
            self.form.levels_list.setEnabled(True)
            self.form.f2k_filename.setEnabled(False)
            self.form.browse.setEnabled(False)

    def browse(self):
        ext = '.f2k'
        from PySide.QtGui import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.f2k_filename.setText(filename)

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
            if self.etabs is None:
                import find_etabs
                self.etabs, filename = find_etabs.find_etabs(software='SAFE', backup=False)
                if (
                    self.etabs is None or
                    filename is None
                    ):
                    return
            self.etabs.area.export_freecad_strips(doc=doc)
            self.etabs.view.refresh_view()
        elif self.form.safe16.isChecked():
            ret = self.export_to_safe_16(doc)
            if ret is None:
                return
        QMessageBox.information(None, "Applied to Software", "Strips Written Successfully.")

    def export_to_safe_16(self, doc):
        filename = self.form.f2k_filename.text()
        if not Path(filename).exists():
            QMessageBox.warning(None, "F2k File", "Please Select a valid F2k filename.")
            return None
        # check input f2k file
        from osafe_import_export.safe_read_write_f2k import get_f2k_version
        with open(filename, 'r') as f:
            content = f.read()
        ver = get_f2k_version(doc=doc, content=content)
        if ver is None:
            QMessageBox.warning(None, "Missing Input F2k", "You don't have a Valid f2k file.")
        elif ver < 14:
            QMessageBox.warning(None, "Version Error", f"The version of input f2k is {ver}, please convert it to version 14 or 16.")
            return 
        from osafe_import_export.safe_read_write_f2k import FreecadReadwriteModel as FRW
        from osafe_funcs import osafe_funcs
        from freecad_funcs import add_to_clipboard

        strips = osafe_funcs.get_objects_of_type("Strip", doc)
        rw = FRW(filename, filename, doc)
        rw.export_freecad_strips(strips)
        rw.safe.write()
        add_to_clipboard(filename)
        return True
    
    def show_help(self):
        from freecad_funcs import show_help
        show_help('import_model.html', 'OSAFE')

    def getStandardButtons(self):
        return 0

    def accept(self):
        Gui.Control.closeDialog()
