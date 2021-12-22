from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtWidgets

import sys
import os
import itertools

import sec

section_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
export_xml_window, xml_base = uic.loadUiType(os.path.join(section_path, 'widgets', 'export.ui'))

useAsDict = {'Beam': 'B', 'Column': 'C', 'Brace': 'C'}
ductilityDict = {'Medium': 'M', 'High': 'H'}


class ExportToXml(xml_base, export_xml_window):
    def __init__(self, sections, parent=None):
        super(ExportToXml, self).__init__()
        self.setupUi(self)
        self.sections = sections
        self.xml_button.clicked.connect(self.select_file)
        for lw in (self.use_as_list, self.ductility_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)

    def accept(self):
        filename = self.xml_path_line.text()
        if not filename:
            return
        extension = self.extension_box.currentText()
        if not filename.endswith(extension):
            filename += f".{extension}"
            self.xml_path_line.setText(filename)

        ductilities = [ductilityDict[item.text()] for item in self.ductility_list.selectedItems()]
        useAss = [useAsDict[item.text()] for item in self.use_as_list.selectedItems()]
        states = [f'{state[0]}{state[1]}' for state in itertools.product(useAss, ductilities)]
        if self.shear_section_checkbox.isChecked():
            states.append('_S')

        sections = []
        for section in self.sections:
            useAs_ductility = section.useAs + section.ductility
            if useAs_ductility in states:
                sections.append(section)
        if extension == "xml":
            sec.Section.exportXml(filename, sections)
        elif extension == "xlsx":
            sec.Section.export_to_pro(filename, sections)

        xml_base.accept(self)

    def select_file(self):
        extension = self.extension_box.currentText()
        filters = "{0} (*.{0});;All files (*.*)".format(extension)
        self.xml_path_line.setText(QFileDialog.getSaveFileName(filter=filters)[0])
        filename = self.xml_path_line.text()
        if not filename:
            return
        extension = self.extension_box.currentText()
        if not filename.endswith(extension):
            filename += f".{extension}"
            self.xml_path_line.setText(filename)
