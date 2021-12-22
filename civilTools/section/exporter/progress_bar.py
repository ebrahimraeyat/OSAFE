from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtWidgets

import sys
import os

section_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
progress_bar_window, progress_bar_base = uic.loadUiType(os.path.join(section_path, 'widgets', 'progress_bar.ui'))


class ProgressBar(progress_bar_base, progress_bar_window):
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__()
        self.setupUi(self)

    def accept(self):
        progress_bar_base.accept(self)
