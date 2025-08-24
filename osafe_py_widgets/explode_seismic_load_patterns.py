from pathlib import Path

import FreeCADGui as Gui

import etabs_obj
from osafe_py_widgets import resource_rc
from PySide.QtGui import QPixmap

punch_path = Path(__file__).parent.parent

class Form:
    def __init__(self, parent=None):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'explode_seismic_load_patterns.ui'))
        self.etabs = etabs_obj.EtabsModel(backup=False)
        self.form.start_button.clicked.connect(self.accept)
        # self.form.close_button.clicked.connect(self.reject)
        
    def accept(self):
        ex = self.form.ex.text()
        epx = self.form.epx.text()
        enx = self.form.enx.text()
        ey = self.form.ey.text()
        epy = self.form.epy.text()
        eny = self.form.eny.text()
        equal_names = {
            'XDir' : ex,
            'XDirPlusE' : epx,
            'XDirMinusE' : enx,
            'YDir' : ey,
            'YDirPlusE' : epy,
            'YDirMinusE' : eny,
            }
        replace_ex = self.form.replace_ex.isChecked()
        replace_ey = self.form.replace_ey.isChecked()
        drift_prefix = self.form.drift_prefix.text()
        drift_suffix = self.form.drift_suffix.text()
        pixmap = QPixmap(str(punch_path / 'Resources' / 'icons' / 'tick.svg'))
        for ret in self.etabs.database.expand_loads(
            equal_names=equal_names,
            replace_ex = replace_ex,
            replace_ey = replace_ey,
            drift_prefix = drift_prefix,
            drift_suffix = drift_suffix,
            ):
            if type(ret) == tuple and len(ret) == 2:
                message, number = ret
                if type(message) == str and type(number) == int:
                    self.form.result_label.setText(message)
                    self.form.progressbar.setValue(number)
                    if message.startswith('Get'):
                        if 'case' in message:
                            self.form.get_loadpat.setPixmap(pixmap)
                        elif 'load combinations' in message:
                            if 'Design' in message:
                                self.form.get_loadcomb.setPixmap(pixmap)
                            else:
                                self.form.get_loadcase.setPixmap(pixmap)
                    elif message.startswith('Apply'):
                        if 'pattern' in message:
                            self.form.get_design_loadcomb.setPixmap(pixmap)
                        elif 'case' in message:
                            self.form.set_loadpat.setPixmap(pixmap)
                        elif 'load combinations' in message:
                            if 'Design' in message:
                                self.form.set_loadcomb.setPixmap(pixmap)
                            else:
                                self.form.set_loadcase.setPixmap(pixmap)
                    elif 'Finished' in message:
                        self.form.set_design_loadcomb.setPixmap(pixmap)
            elif type(ret) == bool:
                if not ret:
                    self.form.result_label.setText("Error Occurred, process did not finished.")
                self.form.start_button.setEnabled(False)
            elif type(ret) == str:
                self.form.result_label.setText(ret)

