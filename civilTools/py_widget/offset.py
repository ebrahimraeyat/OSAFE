import sys
from pathlib import Path

from PyQt5 import QtCore

from PyQt5 import uic
from PyQt5.QtCore import Qt

cfactor_path = Path(__file__).absolute().parent.parent

offset_base, offset_window = uic.loadUiType(cfactor_path / 'widgets' / 'offset.ui')

class OffsetForm(offset_base, offset_window):
    def __init__(self,
            etabs,
            parent=None):
        super(OffsetForm, self).__init__()
        self.setupUi(self)
        unit = etabs.get_current_unit()[1]
        self.distance.setSuffix(f' {unit}')
        self.etabs = etabs

    def accept(self):
        distance = self.distance.value()
        neg = self.negative.isChecked()
        self.etabs.frame_obj.offset_frame(distance, neg)


