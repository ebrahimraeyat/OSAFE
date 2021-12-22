from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtWidgets

import sys
import os
import pickle

section_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
multi_section_window, multi_section_base = uic.loadUiType(os.path.join(section_path, 'widgets', 'multi_section.ui'))


class MultiSection(multi_section_base, multi_section_window):
    def __init__(self, parent=None):
        super(MultiSection, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.tb_width_button.clicked.connect(self.add_tb_width)
        self.tb_thick_button.clicked.connect(self.add_tb_thick)
        self.web_height_button.clicked.connect(self.add_web_height)
        self.web_thick_button.clicked.connect(self.add_web_thick)
        self.dist_button.clicked.connect(self.add_dist)
        self.remove_button.clicked.connect(self.remove_items)
        self.file = os.path.join(section_path, "widgets", "d.dat")
        self.restore_numbers()

    def restore_numbers(self):

        self.data = None
        try:
            self.data = pickle.load(open(self.file, "rb"))
        except:
            pass
        if self.data:
            self.tb_width_list.clear()
            self.tb_thick_list.clear()
            self.web_height_list.clear()
            self.web_thick_list.clear()
            self.section_dist.clear()
            self.tb_width_list.addItems(self.data.get("tb_width_list", ["25"]))
            self.tb_thick_list.addItems(self.data.get("tb_thick_list", ["10"]))
            self.section_dist.addItems(self.data.get("section_dist", ["80"]))
            self.web_height_list.addItems(self.data.get("web_height_list", ["25"]))
            self.web_thick_list.addItems(self.data.get("web_thick_list", ["10"]))
            self.width_box.setValue(self.data.get("width_box_value", 15))
            self.thick_box.setValue(self.data.get("thick_box_value", 6))

    def add_tb_width(self):
        item = self.get_str_value(self.width_box)
        if self.tb_width_list.findItems(item, Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.tb_width_list.addItem(item)

    def add_tb_thick(self):
        item = self.get_str_value(self.thick_box)
        if self.tb_thick_list.findItems(item, Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.tb_thick_list.addItem(item)

    def add_web_height(self):
        item = self.get_str_value(self.width_box)
        if self.web_height_list.findItems(item, Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.web_height_list.addItem(item)

    def add_web_thick(self):
        item = self.get_str_value(self.thick_box)
        if self.web_thick_list.findItems(item, Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.web_thick_list.addItem(item)

    def add_dist(self):
        item = f"{self.dist_box.value():03d}"
        if self.section_dist.findItems(item, Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.section_dist.addItem(item)

    def remove_items(self):
        for lw in (self.tb_width_list, self.tb_thick_list, self.section_dist,
                   self.web_height_list, self.web_thick_list):
            selected_items = lw.selectedItems()
            for item in selected_items:
                lw.takeItem(lw.row(item))

    def get_str_value(self, spinbox):
        return f"{spinbox.value():02d}"

    def get_items(self, qlistwidget):
        l = []
        for i in range(qlistwidget.count()):
            l.append(qlistwidget.item(i).text())

        return l

    def accept(self):
        d = {
            "tb_width_list": self.get_items(self.tb_width_list),
            "tb_thick_list": self.get_items(self.tb_thick_list),
            "web_height_list": self.get_items(self.web_height_list),
            "web_thick_list": self.get_items(self.web_thick_list),
            "section_dist": self.get_items(self.section_dist),
            "width_box_value": self.width_box.value(),
            "thick_box_value": self.thick_box.value(),
        }
        try:
            pickle.dump(d, open(self.file, "wb"))
        except:
            pass
        multi_section_base.accept(self)
