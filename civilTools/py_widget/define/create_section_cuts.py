from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox

cfactor_path = Path(__file__).absolute().parent.parent.parent

section_cut_base, section_cut_window = uic.loadUiType(cfactor_path / 'widgets' / 'define' / 'create_section_cuts.ui')

class SectionCutForm(section_cut_base, section_cut_window):
    def __init__(self, etabs_model, parent=None):
        super(SectionCutForm, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.fill_groups()
        self.create_connections()

    def fill_groups(self):
        groups = self.etabs.group.names()
        self.group.addItems(groups)
        self.group.setCurrentIndex(self.group.count() - 1)

    def create_connections(self):
        self.prefix_name.editingFinished.connect(self.check_prefix)

    def check_prefix(self):
        if len(self.prefix_name.text()) < 1:
            self.prefix_name.setText('SEC')

    def accept(self):
        group = self.group.currentText()
        groups = self.etabs.group.names()
        if not group in groups:
            self.etabs.group.add(group)
        prefix_name = self.prefix_name.text()
        angles_inc = self.angles_inc.value()
        angles = range(0, 180, angles_inc)
        self.etabs.database.create_section_cuts(group, prefix_name, angles)
        super(SectionCutForm, self).accept()
        QMessageBox.information(None, 'Successfull','Successfully written to etabs file.')