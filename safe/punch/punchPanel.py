import re
import os
import FreeCADGui as Gui
import FreeCAD as App
# from PySide import QtGui, QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from safe.punch import geom
from safe.punch import pdf
# from safe.punch.colorbar import ColorMap
abs_path = os.path.split(os.path.abspath(__file__))[0]


class PunchTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.lastDirectory = ''
        App.newDocument("punch")

    def setupUi(self):
        # self.createWidgetsOne()
        self.create_connections()
        self.form.export_excel_button.setIcon(QPixmap(abs_path + "/xlsx.png"))
        self.form.export_pdf_button.setIcon(QPixmap(abs_path + "/pdf.svg"))
        self.form.export_image_button.setIcon(QPixmap(abs_path + "/png.png"))
        self.form.calculate_punch_button.setIcon(QPixmap(abs_path + "/run.svg"))
        self.form.help_button.setIcon(QPixmap(abs_path + "/help.svg"))

    def create_connections(self):
        self.form.excel_button.clicked.connect(self.on_browse)
        self.form.excel_lineedit.textChanged.connect(self.update_shape)
        self.form.calculate_punch_button.clicked.connect(self.calculate_punch)
        self.form.export_excel_button.clicked.connect(self.export_to_excel)
        self.form.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.form.export_image_button.clicked.connect(self.export_to_image)
        self.form.help_button.clicked.connect(self.help)

    def clearAll(self):
        doc = App.getDocument("punch")
        if doc is None:
            return
        objs = doc.Objects
        if objs:
            group = objs[0]
            group.removeObjectsFromDocument()
            doc.removeObject(group.Label)

    def update_shape(self):
        filename = self.form.excel_lineedit.text()
        self.shape = geom.Geom(filename)
        combos = self.shape.load_combinations['Combo'].unique()
        self.form.load_combination_box.addItems(list(combos))
        self.form.safe_prop_browser.setText(self.shape._safe.__str__())
        self.shape.plot()
        self.form.calculate_punch_button.setEnabled(True)

    def calculate_punch(self):
        self.ratios_df = self.shape.punch_ratios()
        # self.add_color_map()
        self.form.export_excel_button.setEnabled(True)
        self.form.export_pdf_button.setEnabled(True)
        self.form.export_image_button.setEnabled(True)

    # def add_color_map(self):
    #     ratios = self.ratios_df.loc['Max']
    #     min_ = ratios.min()
    #     max_ = ratios.max()
    #     mw = Gui.getMainWindow()  # access the main window
    #     ColorMapWidget = QDockWidget()  # create a new dockwidget
    #     ColorMapWidget.setWidget(ColorMap(min_, max_))  # load the Ui script
    #     mw.addDockWidget(Qt.RightDockWidgetArea, ColorMapWidget)  # add the widget to the main window

    def on_browse(self):
        filename = self.getFilename(['xls', 'xlsx'])
        if not filename:
            return
        self.form.excel_lineedit.setText(filename)

    def help(self):
        import webbrowser
        webbrowser.open_new(abs_path + '/Help.pdf')

    def export_to_excel(self):
        filters = "Excel (*.xls *.xlsx)"
        filename, _ = QFileDialog.getSaveFileName(self.form, 'select file',
                                                  self.lastDirectory, filters)
        if not filename:
            return
        if not '.xls' in filename:
            filename += ".xlsx"
        self.ratios_df.to_excel(filename)

    def export_to_pdf(self):
        filename = self.get_save_filename('.pdf')
        doc = App.getDocument("punch")
        pdf.createPdf(doc, filename)

    def export_to_image(self):
        filename = self.get_save_filename('.png')
        doc = App.getDocument("punch")
        pdf.createPdf(doc, filename)

    def getLastSaveDirectory(self, f):
        return os.sep.join(f.split(os.sep)[:-1])

    def getFilename(self, prefixes):
        filters = 'Excel ('
        for prefix in prefixes:
            filters += f"*.{prefix} "
        filters += ')'
        filename, _ = QFileDialog.getOpenFileName(self.form, 'select file',
                                                  self.lastDirectory, filters)
        if not filename:
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename

    def get_save_filename(self, ext):
        filters = f"{ext[:-1]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(self.form, 'select file',
                                                  self.lastDirectory, filters)
        if not filename:
            return
        if not ext in filename:
            filename += ext
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename


if __name__ == '__main__':
    panel = PunchTaskPanel()
