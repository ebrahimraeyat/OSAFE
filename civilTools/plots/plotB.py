# -*- coding: utf-8 -*-

import sys
from PySide2.QtGui import QWidget, QVBoxLayout, QApplication
import pyqtgraph as pg
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class PlotB(QWidget):

    def __init__(self, parent=None):
        super(PlotB, self).__init__(parent)

        self.win = pg.GraphicsWindow()
        self.p = self.createAxis(self.win)
        my_layout = QVBoxLayout()
        my_layout.addWidget(self.win)
        self.setLayout(my_layout)

    def createAxis(self, window):
        p = window.addPlot()
        p.setLabel('bottom', text='T', units='Sec')
        p.setLabel('left', text="N,  B1, B")
        p.showGrid(x=True, y=True)
        p.setXRange(0, 4.5, padding=0)
        p.setYRange(0, 4, padding=0)
        return p


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = PlotB()
    form.show()
    app.exec_()