from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt

cfactor_path = Path(__file__).absolute().parent.parent

base, window = uic.loadUiType(cfactor_path / 'widgets' / 'torsion.ui')

class Form(base, window):
    def __init__(self, etabs_model, parent=None):
        super(Form, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.fill_xy_loadcase_names()

    def fill_xy_loadcase_names(self):
        x_names, y_names = self.etabs.load_patterns.get_load_patterns_in_XYdirection()
        drift_load_patterns = self.etabs.load_patterns.get_drift_load_pattern_names()
        all_load_case = self.etabs.SapModel.Analyze.GetCaseStatus()[1]
        x_names = set(x_names).intersection(set(all_load_case))
        y_names = set(y_names).intersection(set(all_load_case))
        self.x_loadcase_list.addItems(x_names)
        self.y_loadcase_list.addItems(y_names)
        for lw in (self.x_loadcase_list, self.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
        for name in drift_load_patterns:
            if name in x_names:
                matching_items = self.x_loadcase_list.findItems(name, Qt.MatchExactly)
            elif name in y_names:
                matching_items = self.y_loadcase_list.findItems(name, Qt.MatchExactly)
            for item in matching_items:
                item.setCheckState(Qt.Unchecked)
