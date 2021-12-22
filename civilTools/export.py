# -*- coding: utf-8 -*-

from PySide2.QtGui import *
from PySide2.QtCore import *
import os
from functools import reduce
# import pyqtgraph as pg
from exporter import export_to_word as word
from exporter import config
from pathlib import Path
import sys

def getLastSaveDirectory(f):
    f = str(f)
    return os.sep.join(f.split(os.sep)[:-1])


class Export:

    def __init__(self, widget, dirty, lastDirectory, building):
        self.widget = widget
        self.dirty = dirty
        self.lastDirectory = lastDirectory
        self.building = building

    def to_word(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        filters = "docx(*.docx)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, 'Word خروجی به',
                                                  self.lastDirectory, filters)
        if filename == '':
            return
        if not filename.endswith(".docx"):
            filename += ".docx"
        self.lastDirectory = getLastSaveDirectory(filename)
        word.export(self.building, filename)

    def to_json(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        filters = "json(*.json)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, 'save project',
                                                  self.lastDirectory, filters)
        if filename == '':
            return
        if not filename.endswith('.json'):
            filename += '.json'
        self.lastDirectory = getLastSaveDirectory(filename)
        config.save(self.widget, filename)


class ExportGraph:
    def __init__(self, widget, lastDirectory, p):
        self.widget = widget
        self.lastDirectory = lastDirectory
        self.p = widget.p

    def to_image(self):
        filters = "png(*.png);;jpg(*.jpg);;bmp(*.bmp);;eps(*.eps);;tif(*.tif);;jpeg(*.jpeg)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u'خروجی منحنی ضریب بازتاب',
                                                  self.lastDirectory, filters)
        if filename == '':
            return
        self.lastDirectory = getLastSaveDirectory(filename)
        exporter = pg.exporters.ImageExporter(self.p)
        exporter.parameters()['width'] = 1920   # (note this also affects height parameter)
        #exporter.parameters()['height'] = 600
        # save to file
        exporter.export(filename)

    def to_csv(self):
        filters = "txt(*.txt)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u'Export Spectrum',
                                                  self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = getLastSaveDirectory(filename)
        A = self.widget.final_building.acc
        I = self.widget.final_building.importance_factor
        Rux = self.widget.final_building.x_system.Ru
        Ruy = self.widget.final_building.y_system.Ru
        data = []
        for c in self.p.curves:
            if c.name() == 'B':
                data.append(c.getData())

        sep = '\t'
        if Rux == Ruy:
            Rs = (Rux,)
            dirs = ('',)
        else:
            Rs = (Rux, Ruy)
            dirs = ('_x', '_y')
        for R, dir_ in zip(Rs, dirs):
            fname = f'{filename[:-4]}{dir_}{filename[-4:]}'
            fd = open(fname, 'w')
            i = 0
            numFormat = '%0.10g'
            numRows = reduce(max, [len(d[0]) for d in data])
            for i in range(numRows):
                for d in data:
                    if i < len(d[0]):
                        c = A * d[1][i] * I / R
                        fd.write(numFormat % d[0][i] + sep + numFormat % c)
                fd.write('\n')
            fd.close()
