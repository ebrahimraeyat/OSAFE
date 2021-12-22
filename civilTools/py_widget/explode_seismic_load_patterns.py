from pathlib import Path

from PyQt5 import uic
from PyQt5.QtGui import QPixmap

cfactor_path = Path(__file__).absolute().parent.parent

base, window = uic.loadUiType(cfactor_path / 'widgets' / 'explode_seismic_load_patterns.ui')


class Form(base, window):
    def __init__(self, etabs_model, parent=None):
        super(Form, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.start_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)
        
    def accept(self):
        ex = self.ex.text()
        epx = self.epx.text()
        enx = self.enx.text()
        ey = self.ey.text()
        epy = self.epy.text()
        eny = self.eny.text()
        equal_names = {
            'XDir' : ex,
            'XDirPlusE' : epx,
            'XDirMinusE' : enx,
            'YDir' : ey,
            'YDirPlusE' : epy,
            'YDirMinusE' : eny,
            }
        replace_ex = self.replace_ex.isChecked()
        replace_ey = self.replace_ey.isChecked()
        drift_prefix = self.drift_prefix.text()
        drift_suffix = self.drift_suffix.text()
        pixmap = QPixmap(str(cfactor_path.parent.parent / 'images' / 'tick.svg'))
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
                    self.result_label.setText(message)
                    self.progressbar.setValue(number)
                    if message.startswith('Get'):
                        if 'case' in message:
                            self.get_loadpat.setPixmap(pixmap)
                        elif 'load combinations' in message:
                            if 'Design' in message:
                                self.get_loadcomb.setPixmap(pixmap)
                            else:
                                self.get_loadcase.setPixmap(pixmap)
                    elif message.startswith('Apply'):
                        if 'pattern' in message:
                            self.get_design_loadcomb.setPixmap(pixmap)
                        elif 'case' in message:
                            self.set_loadpat.setPixmap(pixmap)
                        elif 'load combinations' in message:
                            if 'Design' in message:
                                self.set_loadcomb.setPixmap(pixmap)
                            else:
                                self.set_loadcase.setPixmap(pixmap)
                    elif 'Finished' in message:
                        self.set_design_loadcomb.setPixmap(pixmap)
            elif type(ret) == bool:
                if not ret:
                    self.result_label.setText("Error Occurred, process did not finished.")
                self.start_button.setEnabled(False)
            elif type(ret) == str:
                self.result_label.setText(ret)

