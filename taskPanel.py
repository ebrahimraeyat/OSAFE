
import re
import os
import FreeCADGui as Gui
import FreeCAD as App
# from PySide import QtGui, QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sec
# from plot_profiles import PlotSectionAndEqSection
from plot_profiles import PlotSectionAndEqSection

from sectionUtils import Paths
ipesProp = sec.Ipe.createStandardIpes()
unpsProp = sec.Unp.createStandardUnps()
cpesProp = sec.Cpe.createStandardCpes()


class SectionTaskPanel:
    sectionProp = {'IPE': ipesProp, 'UNP': unpsProp, 'CPE': cpesProp}
    useAsDict = {'تیر': 'B', 'ستون': 'C'}
    ductilityDict = {'متوسط': 'M', 'زیاد': 'H'}
    doubleList1 = ['تک', 'دوبل', 'سوبل']
    doubleList2 = [[False, False], [True, False], [False, True]]
    doubleDict = dict(zip(doubleList1, doubleList2))


    def __init__(self):
        # ui = Paths.modulePath() + "/taskPanel.ui"
        self.form = Gui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        App.newDocument("all_section")
        App.newDocument("current_section")
        self.lastDirectory = ''
        # self.setupUi()
        # self.skip = False

    # def accept(self):
    #     return True

    # def reject(self):
    #     return True

    # def clicked(self, index):
    #     pass

    # def open(self):
    #     pass

    # def needsFullSpace(self):
    #     return True

    # def isAllowedAlterSelection(self):
    #     return False

    # def isAllowedAlterView(self):
    #     return True

    # def isAllowedAlterDocument(self):
    #     return False

    # def helpRequested(self):
    #     pass

    def setupUi(self):
        self.last_sectionBox_index = {'IPE': 4, 'UNP': 4, 'CPE':4}
        self.currentSectionProp = None
        self.createWidgetsOne()
        self.create_connections()
        self.updateSectionShape()
        Gui.SendMsgToActiveView("ViewFit")
    
    # def widget(self, class_id, name):
    #     """Return the selected widget.

    #     Keyword arguments:
    #     class_id -- Class identifier
    #     name -- Name of the widget
    #     """
    #     mw = self.getMainWindow()
    #     form = mw.findChild(QtGui.QWidget, "TaskPanel")
    #     return form.findChild(class_id, name)

    # def retranslateUi(self):
    #     """ Set the user interface locale strings.
    #     """
    #     self.form.setWindowTitle(QtGui.QApplication.translate(
    #         "plot_labels",
    #         "Set labels",
    #         None))
    #     self.widget(QtGui.QLabel, "axesLabel").setText(
    #         QtGui.QApplication.translate("plot_labels",
    #                                      "Active axes",
    #                                      None))
    #     self.widget(QtGui.QLabel, "titleLabel").setText(
    #         QtGui.QApplication.translate("plot_labels",
    #                                      "Title",
    #                                      None))
    #     self.widget(QtGui.QLabel, "xLabel").setText(
    #         QtGui.QApplication.translate("plot_labels",
    #                                      "X label",
    #                                      None))
    #     self.widget(QtGui.QLabel, "yLabel").setText(
    #         QtGui.QApplication.translate("plot_labels",
    #                                      "Y label",
    #                                      None))
    #     self.widget(QtGui.QSpinBox, "axesIndex").setToolTip(QtGui.QApplication.translate(
    #         "plot_labels",
    #         "Index of the active axes",
    #         None))
    #     self.widget(QtGui.QLineEdit, "title").setToolTip(
    #         QtGui.QApplication.translate(
    #             "plot_labels",
    #             "Title (associated to active axes)",
    #             None))
    #     self.widget(QtGui.QSpinBox, "titleSize").setToolTip(
    #         QtGui.QApplication.translate(
    #             "plot_labels",
    #             "Title font size",
    #             None))
    #     self.widget(QtGui.QLineEdit, "titleX").setToolTip(
    #         QtGui.QApplication.translate(
    #             "plot_labels",
    #             "X axis title",
    #             None))
    #     self.widget(QtGui.QSpinBox, "xSize").setToolTip(
    #         QtGui.QApplication.translate(
    #             "plot_labels",
    #             "X axis title font size",
    #             None))
    #     self.widget(QtGui.QLineEdit, "titleY").setToolTip(
    #         QtGui.QApplication.translate(
    #             "plot_labels",
    #             "Y axis title",
    #             None))
    #     self.widget(QtGui.QSpinBox, "ySize").setToolTip(
    #         QtGui.QApplication.translate(
    #             "plot_labels",
    #             "Y axis title font size",
    #             None))

    def resizeColumns(self, tableView=None):
        for column in (sec.NAME, sec.AREA,
                       sec.ASY, sec.ASX, sec.IX, sec.IY, sec.ZX, sec.ZY,
                         sec.BF, sec.TF, sec.D, sec.TW, sec.Sx, sec.Sy, sec.RX, sec.RY):
            tableView.resizeColumnToContents(column)

    def create_connections(self):
        self.form.sectionTypeBox.currentIndexChanged.connect(self.updateGui)
        self.form.sectionTypeBox.currentIndexChanged.connect(self.setSectionLabels)
        self.form.lhSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.thSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.lwSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.twSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.lvSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.tvSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.distSpinBox.valueChanged.connect(self.updateSectionShape)
        self.form.addTBPLGroupBox.clicked.connect(self.updateSectionShape)
        self.form.addLRPLGroupBox.clicked.connect(self.updateSectionShape)
        self.form.addWebPLGroupBox.toggled.connect(self.updateSectionShape)
        self.form.sectionsBox.currentIndexChanged.connect(self.updateSectionShape)
        self.form.doubleBox.currentIndexChanged.connect(self.updateSectionShape)
        # self.form.ductilityBox.currentIndexChanged.connect(self.updateSectionShape)
        # self.form.useAsBox.currentIndexChanged.connect(self.updateSectionShape)
        # self.form.convert_type_radio_button.toggled.connect(self.updateSectionShape)
    

    def createWidgetsOne(self):
        self.model1 = sec.SectionTableModel("section.dat")
        # self.ui.tableView1.setLayoutDirection(Qt.LeftToRight)
        self.form.tableView1.setModel(self.model1)
        self.form.clear_all_Button.clicked.connect(self.clear_sections)
        # self.deleteSectionButton.clicked.connect(self.removeSection)
        self.form.saveToXml1Button.clicked.connect(self.saveToXml1)
        self.form.excel_button.clicked.connect(self.save_to_excel)
        self.form.remove_Button.clicked.connect(self.removeSection)
        # self.save_to_autocad_Button.clicked.connect(self.save_to_autocad_script_format)
        # self.saveToFileButton.clicked.connect(self.export_to_dat)
        # self.load_from_dat_button.clicked.connect(self.load_from_dat)
        # self.addSectionButton.clicked.connect(self.addSection)
        self.form.calculate_Button.clicked.connect(self.acceptOne)
        self.form.doubleBox.addItems(self.doubleList1)
        self.form.doubleBox.setCurrentIndex(1)
        self.form.sectionTypeBox.addItems(sorted(self.sectionProp.keys()))
        sectionType = self.currentSectionType()
        self.form.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.form.sectionsBox.setCurrentIndex(4)
        
    # def onAxesId(self, value):
    #     """ Executed when axes index is modified. """
    #     if not self.skip:
    #         self.skip = True
    #         # No active plot case
    #         plt = Plot.getPlot()
    #         if not plt:
    #             self.updateUI()
    #             self.skip = False
    #             return
    #         # Get again all the subwidgets (to avoid PySide Pitfalls)
    #         mw = self.getMainWindow()
    #         form = mw.findChild(QtGui.QWidget, "TaskPanel")
    #         form.axId = self.widget(QtGui.QSpinBox, "axesIndex")

    #         form.axId.setMaximum(len(plt.axesList))
    #         if form.axId.value() >= len(plt.axesList):
    #             form.axId.setValue(len(plt.axesList) - 1)
    #         # Send new control to Plot instance
    #         plt.setActiveAxes(form.axId.value())
    #         self.updateUI()
    #         self.skip = False

    # def onLabels(self):
    #     """ Executed when labels have been modified. """
    #     plt = Plot.getPlot()
    #     if not plt:
    #         self.updateUI()
    #         return
    #     # Get again all the subwidgets (to avoid PySide Pitfalls)
    #     mw = self.getMainWindow()
    #     form = mw.findChild(QtGui.QWidget, "TaskPanel")
    #     form.title = self.widget(QtGui.QLineEdit, "title")
    #     form.xLabel = self.widget(QtGui.QLineEdit, "titleX")
    #     form.yLabel = self.widget(QtGui.QLineEdit, "titleY")

    #     Plot.title(unicode(form.title.text()))
    #     Plot.xlabel(unicode(form.xLabel.text()))
    #     Plot.ylabel(unicode(form.yLabel.text()))
    #     plt.update()

    # def onFontSizes(self, value):
    #     """ Executed when font sizes have been modified. """
    #     # Get apply environment
    #     plt = Plot.getPlot()
    #     if not plt:
    #         self.updateUI()
    #         return
    #     # Get again all the subwidgets (to avoid PySide Pitfalls)
    #     mw = self.getMainWindow()
    #     form = mw.findChild(QtGui.QWidget, "TaskPanel")
    #     form.titleSize = self.widget(QtGui.QSpinBox, "titleSize")
    #     form.xSize = self.widget(QtGui.QSpinBox, "xSize")
    #     form.ySize = self.widget(QtGui.QSpinBox, "ySize")

    #     ax = plt.axes
    #     ax.title.set_fontsize(form.titleSize.value())
    #     ax.xaxis.label.set_fontsize(form.xSize.value())
    #     ax.yaxis.label.set_fontsize(form.ySize.value())
    #     plt.update()

    # def onMdiArea(self, subWin):
    #     """ Executed when window is selected on mdi area.

    #     Keyword arguments:
    #     subWin -- Selected window.
    #     """
    #     plt = Plot.getPlot()
    #     if plt != subWin:
    #         self.updateUI()

    # def updateUI(self):
    #     """ Setup UI controls values if possible """
    #     # Get again all the subwidgets (to avoid PySide Pitfalls)
    #     mw = self.getMainWindow()
    #     form = mw.findChild(QtGui.QWidget, "TaskPanel")
    #     form.axId = self.widget(QtGui.QSpinBox, "axesIndex")
    #     form.title = self.widget(QtGui.QLineEdit, "title")
    #     form.titleSize = self.widget(QtGui.QSpinBox, "titleSize")
    #     form.xLabel = self.widget(QtGui.QLineEdit, "titleX")
    #     form.xSize = self.widget(QtGui.QSpinBox, "xSize")
    #     form.yLabel = self.widget(QtGui.QLineEdit, "titleY")
    #     form.ySize = self.widget(QtGui.QSpinBox, "ySize")

    #     plt = Plot.getPlot()
    #     form.axId.setEnabled(bool(plt))
    #     form.title.setEnabled(bool(plt))
    #     form.titleSize.setEnabled(bool(plt))
    #     form.xLabel.setEnabled(bool(plt))
    #     form.xSize.setEnabled(bool(plt))
    #     form.yLabel.setEnabled(bool(plt))
    #     form.ySize.setEnabled(bool(plt))
    #     if not plt:
    #         return
    #     # Ensure that active axes is correct
    #     index = min(form.axId.value(), len(plt.axesList) - 1)
    #     form.axId.setValue(index)
    #     # Store data before starting changing it.

    #     ax = plt.axes
    #     t = ax.get_title()
    #     x = ax.get_xlabel()
    #     y = ax.get_ylabel()
    #     tt = ax.title.get_fontsize()
    #     xx = ax.xaxis.label.get_fontsize()
    #     yy = ax.yaxis.label.get_fontsize()
    #     # Set labels
    #     form.title.setText(t)
    #     form.xLabel.setText(x)
    #     form.yLabel.setText(y)
    #     # Set font sizes
    #     form.titleSize.setValue(tt)
    #     form.xSize.setValue(xx)
    #     form.ySize.setValue(yy)

    def setSectionLabels(self):
        sectionType = self.currentSectionType()
        #self.last_sectionBox_index[sectionType] = self.sectionsBox.currentIndex()
        old_state = bool(self.form.sectionsBox.blockSignals(True))
        self.form.sectionsBox.clear()
        self.form.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.form.sectionsBox.blockSignals(old_state)
        self.form.sectionsBox.setCurrentIndex(self.last_sectionBox_index[sectionType])

    def updateGui(self):
        index = self.form.doubleBox.currentIndex()
        sectionType = self.currentSectionType()
        if sectionType == 'UNP':
            self.form.doubleBox.removeItem(2)
            if index == 2:
                self.form.doubleBox.setCurrentIndex(index - 1)
            self.form.addWebPLGroupBox.setChecked(False)
            self.form.addWebPLGroupBox.setEnabled(False)
        elif sectionType == 'IPE' or 'CPE':
            if self.form.doubleBox.count() < 3:
                self.form.doubleBox.addItem(self.doubleList1[-1])
            self.form.addWebPLGroupBox.setEnabled(True)

    def getSectionLabels(self, sectionType='IPE'):
        if sectionType == 'IPE':
            sections = ipesProp.values()
        elif sectionType == 'UNP':
            sections = unpsProp.values()
        elif sectionType == 'CPE':
            sections = cpesProp.values()

        sectionNames = [section.name for section in sections]
        return sorted(sectionNames)

    def currentSectionType(self):
        return str(self.form.sectionTypeBox.currentText())

    def currentSection(self):
        sectionIndex = self.sectionsBox.currentIndex()
        sectionType = self.currentSectionType()
        return self.sectionProp[sectionType].values()[sectionIndex]

    def currentSectionOne(self):
        lh = self.form.lhSpinBox.value() * 10
        th = self.form.thSpinBox.value()
        lv = self.form.lvSpinBox.value() * 10
        tv = self.form.tvSpinBox.value()
        lw = self.form.lwSpinBox.value() * 10
        tw = self.form.twSpinBox.value()
        dist = self.form.distSpinBox.value()
        isTBPlate = self.form.addTBPLGroupBox.isChecked()
        isLRPlate = self.form.addLRPLGroupBox.isChecked()
        isWebPlate = self.form.addWebPLGroupBox.isChecked()
        useAs = self.useAsDict[self.form.useAsBox.currentText()]
        ductility = self.ductilityDict[self.form.ductilityBox.currentText()]
        isDouble = self.doubleDict[self.form.doubleBox.currentText()][0]
        isSouble = self.doubleDict[self.form.doubleBox.currentText()][1]
        sectionSize = int(re.sub("[^0-9]", "", self.form.sectionsBox.currentText()))
        sectionType = self.currentSectionType()
        convert_type = 'slender'
        if self.form.convert_type_radio_button.isChecked():
            convert_type = "shear"
        return (lh, th, lv, tv, lw, tw, dist, isTBPlate, isLRPlate, isWebPlate, useAs, ductility, isDouble,
        isSouble, sectionSize, sectionType, convert_type)

    def acceptOne(self):
        #section = self.currentSectionOne()
        #if not section.name in self.model1.names:
        self.currentSection = sec.createSection(self.currentSectionProp)
        self.model1.beginResetModel()
        self.model1.sections.append(self.currentSection)
        self.model1.endResetModel()
        #del section

        self.resizeColumns(self.form.tableView1)
        self.model1.dirty = True

    def updateSectionShape(self):
        self.clearAll()
        self.currentSectionProp = self.currentSectionOne()
        shape = PlotSectionAndEqSection(self.currentSectionProp, len(self.model1.sections))
        shape.plot()

    def clearAll(self):
        doc = App.getDocument("current_section")
        if doc is None: return
        for obj in doc.Objects:
            doc.removeObject(obj.Name)

    def removeSection(self):
        index = self.form.tableView1.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        name = self.model1.data(
                        self.model1.index(row, sec.NAME))
        if (QMessageBox.question(self.form, "sections - Remove",
                f"Remove section {name}?",
                QMessageBox.Yes|QMessageBox.No) ==
                QMessageBox.No):
            return

        self.model1.removeRows(row)
        self.resizeColumns(self.form.tableView1)

    def clear_sections(self):
        if self.model1.sections == []:
            return
        if (QMessageBox.question(self.form, "sections - Remove", "همه مقاطع حذف شوند؟",
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
            return
        self.model1.beginResetModel()
        self.model1.sections = []
        self.model1.endResetModel()
        self.model1.names = set()
        # self.model1.dirty = False

    def saveToXml1(self):
        #if not self.model1.dirty:
            #QMessageBox.warning(self, 'خروجی', 'نتیجه ای جهت ارسال وجود ندارد')
            #return
        filename = self.getFilename(['xml'])
        if not filename:
            return
        if not filename.endswith('xml'):
            filename += '.xml'
        sec.Section.exportXml(filename , self.model1.sections)

    def save_to_excel(self):
        filename = self.getFilename(['xlsx'])
        if not filename:
            return
        if not filename.endswith('xlsx'):
            filename += '.xlsx'
        sec.Section.export_to_excel(filename , self.model1.sections)

    def getLastSaveDirectory(self, f):
        return os.sep.join(f.split(os.sep)[:-1])

    def getFilename(self, prefixes):
        filters = ''
        for prefix in prefixes:
            filters += "{}(*.{})".format(prefix, prefix)
        filename, _ = QFileDialog.getSaveFileName(self.form , 'خروجی',
                                               self.lastDirectory, filters)

        if not filename:
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename
       

# def createTask():
#     panel = SectionTaskPanel()
#     Gui.Control.showDialog(panel)
#     if panel.setupUi():
#         Gui.Control.closeDialog(panel)
#         return None
#     return panel
