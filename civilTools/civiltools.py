# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

civiltools_path = Path(__file__).absolute().parent
sys.path.insert(0, str(civiltools_path))
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import loadUiType
from db import ostanha
from building.build import *
from models import *
# import pyqtgraph as pg
# from plots.plotB import PlotB as pl
import export
from exporter import config



branch = 'v6'

rTable = RFactorTable()
systemTypes = rTable.getSystemTypes()


class Ui(QDialog, loadUiType(str(civiltools_path / 'widgets' / 'cfactor.ui'))[0]):

    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.dirty = False
        self.lastDirectory = ''
        self.printer = None
        self.create_widgets()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.structure_properties_table.setModel(self.structure_model)
        self.resizeColumns()
        self.create_connections()
        # self.add_actions()
        self.load_settings()
        self.load_config()
        self.calculate()

    def create_connections(self):
        self.calculate_button.clicked.connect(self.calculate)
        self.x_treeWidget.itemActivated.connect(self.xactivate)
        self.ostanBox.currentIndexChanged.connect(self.set_shahrs_of_current_ostan)
        self.shahrBox.currentIndexChanged.connect(self.setA)

    def resizeColumns(self):
        for column in (X, Y):
            self.structure_properties_table.resizeColumnToContents(column)

    def create_widgets(self):
        ostans = ostanha.ostans.keys()
        self.ostanBox.addItems(ostans)
        self.set_shahrs_of_current_ostan()
        self.setA()
        #
        # # curve widget
        # self.curveBWidget = pl()
        # self.p = self.curveBWidget.p
        # self.curveBWidget.setMinimumSize(450, 300)
        # draw_layout = QVBoxLayout()
        # draw_layout.addWidget(self.curveBWidget)
        # self.draw_frame.setLayout(draw_layout)

        for i in range(5):
            self.soilPropertiesTable.setSpan(i, 0, 1, 2)
        iterator = QTreeWidgetItemIterator(self.x_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.x_treeWidget.setCurrentItem(item, 0)
                break
            i += 1
        iterator = QTreeWidgetItemIterator(self.y_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.y_treeWidget.setCurrentItem(item, 0)
                break
            i += 1

    def closeEvent(self, event):
        qsettings = QSettings("civiltools", "cfactor")
        qsettings.setValue("geometry", self.saveGeometry())
        # qsettings.setValue("pos", self.pos())
        # qsettings.setValue("size", self.size())
        qsettings.setValue("hsplitter", self.hsplitter.saveState())
        qsettings.setValue("v1splitter", self.v1splitter.saveState())
        qsettings.setValue("v2splitter", self.v2splitter.saveState())
        self.save_config()
        self.set_site_and_building_props()
        event.accept()

    def set_site_and_building_props(self):
        import FreeCAD
        doc = FreeCAD.ActiveDocument
        if hasattr(doc, 'Site'):
            site = doc.Site
            building = doc.BuildingPart
            self.add_properties(site, building)
            site.risk_level = self.final_building.risk_level
            site.soil = self.final_building.soilType
            site.City = self.final_building.city
            building.importance_factor = self.final_building.importance_factor
            if self.final_building.results[0]:
                building.cx = self.final_building.results[1]
                building.cy = self.final_building.results[2]
            building.kx = self.final_building.kx
            building.ky = self.final_building.ky
            if self.final_building.results_drift[0]:
                building.cx_drift = self.final_building.results_drift[1]
                building.cy_drift = self.final_building.results_drift[2]
            building.kx_drift = self.final_building.kx_drift
            building.ky_drift = self.final_building.ky_drift
            building.cdx = self.final_building.x_system.cd
            building.cdy = self.final_building.y_system.cd
            doc.recompute()


    def add_properties(self, site, building):
        if not hasattr(site, 'risk_level'):
            site.addProperty(
                'App::PropertyString',
                'risk_level',
                'CivilTools',
            )
        if not hasattr(site, 'soil'):
            site.addProperty(
                'App::PropertyString',
                'soil',
                'CivilTools',
            )
        if not hasattr(building, 'importance_factor'):
            building.addProperty(
                'App::PropertyFloat',
                'importance_factor',
                'CivilTools',
                )
        if not hasattr(building, 'cx'):
            building.addProperty(
                'App::PropertyFloat',
                'cx',
                'XResults',
                )
        if not hasattr(building, 'cy'):
            building.addProperty(
                'App::PropertyFloat',
                'cy',
                'YResults',
                )
        if not hasattr(building, 'kx'):
            building.addProperty(
                'App::PropertyFloat',
                'kx',
                'XResults',
                )
        if not hasattr(building, 'ky'):
            building.addProperty(
                'App::PropertyFloat',
                'ky',
                'YResults',
                )
        if not hasattr(building, 'cx_drift'):
            building.addProperty(
                'App::PropertyFloat',
                'cx_drift',
                'XResults',
                )
        if not hasattr(building, 'cy_drift'):
            building.addProperty(
                'App::PropertyFloat',
                'cy_drift',
                'YResults',
                )
        if not hasattr(building, 'kx_drift'):
            building.addProperty(
                'App::PropertyFloat',
                'kx_drift',
                'XResults',
                )
        if not hasattr(building, 'ky_drift'):
            building.addProperty(
                'App::PropertyFloat',
                'ky_drift',
                'YResults',
                )
        if not hasattr(building, 'cdx'):
            building.addProperty(
                'App::PropertyFloat',
                'cdx',
                'XLatetalSystem',
                )
        if not hasattr(building, 'cdy'):
            building.addProperty(
                'App::PropertyFloat',
                'cdy',
                'YLateralSystem',
                )

            
            # city = self.get_current_shahr()
            # height = self.HSpinBox.value()
            # importance_factor = float(self.IBox.currentText())
            # soil = self.get_current_soil_type()
            # noStory = self.storySpinBox.value()
            # x_system = self.xactivate()
            # y_system = self.yactivate()
            # if not x_system and y_system:
            #     return None
            # xSystemType, xLateralType = x_system[0], x_system[1]
            # ySystemType, yLateralType = y_system[0], y_system[1]
            # xSystem = StructureSystem(xSystemType, xLateralType, "X")
            # ySystem = StructureSystem(ySystemType, yLateralType, "Y")
            # self.setInfillCheckBoxStatus(xSystem, ySystem)
            # Tan = self.getTAnalatical()
            # useTan = Tan[0]
            # xTan = Tan[1]
            # yTan = Tan[2]
            # is_infill = self.infillCheckBox.isChecked()
    def load_settings(self):
        qsettings = QSettings("civiltools", "cfactor")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        # self.restoreState(qsettings.value("saveState", self.saveState()))
        # self.move(qsettings.value("pos", self.pos()))
        # self.resize(qsettings.value("size", self.size()))
        self.hsplitter.restoreState(qsettings.value("hsplitter", self.hsplitter.saveState()))
        self.v1splitter.restoreState(qsettings.value("v1splitter", self.v1splitter.saveState()))
        self.v2splitter.restoreState(qsettings.value("v2splitter", self.v2splitter.saveState()))

    def load_config(self, json_file=None):
        if not json_file:
            appdata_dir = Path(os.getenv('APPDATA'))
            cfactor_dir = appdata_dir / 'civiltools' / 'cfactor'
            if not cfactor_dir.exists():
                return
            else:
                json_file = cfactor_dir / 'cfactor.json'
                if not json_file.exists():
                    return
        config.load(self, json_file)

    def save_config(self, json_file=None):
        if not json_file:
            appdata_dir = Path(os.getenv('APPDATA'))
            civiltoos_dir = appdata_dir / 'civiltools'
            if not civiltoos_dir.exists():
                civiltoos_dir.mkdir()
            cfactor_dir = civiltoos_dir / 'cfactor'
            if not cfactor_dir.exists():
                cfactor_dir.mkdir()
            json_file = cfactor_dir / 'cfactor.json'
        config.save(self, json_file)

    def ok_to_continue(self, title='save config?', message='save configuration file?'):
        return QMessageBox.question(self, title, message,
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

    def xactivate(self):
        if self.x_treeWidget.currentItem().parent():
            system = self.x_treeWidget.currentItem().parent().text(0)
            lateral = self.x_treeWidget.currentItem().text(0)
            self.y_treeWidget.scrollToItem(self.x_treeWidget.currentItem())
            return (system, lateral)
        return None

    def yactivate(self):
        if self.y_treeWidget.currentItem().parent():
            system = self.y_treeWidget.currentItem().parent().text(0)
            lateral = self.y_treeWidget.currentItem().text(0)
            return (system, lateral)
        return None

    def get_current_ostan(self):
        return self.ostanBox.currentText()

    def get_current_shahr(self):
        return self.shahrBox.currentText()

    def get_shahrs_of_current_ostan(self, ostan):
        '''return shahrs of ostan'''
        return ostanha.ostans[ostan].keys()

    def set_shahrs_of_current_ostan(self):
        self.shahrBox.clear()
        ostan = self.get_current_ostan()
        shahrs = self.get_shahrs_of_current_ostan(ostan)
        # shahrs.sort()
        self.shahrBox.addItems(shahrs)

    def setA(self):
        sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
        ostan = self.get_current_ostan()
        shahr = self.get_current_shahr()
        try:
            A = int(ostanha.ostans[ostan][shahr][0])
            self.accText.setText(sotoh[A - 1])
        except KeyError:
            pass

    def get_current_soil_type(self):
        return str(self.soilType.currentText())

    def setInfillCheckBoxStatus(self, xSystem, ySystem):
        infill = xSystem.is_infill and ySystem.is_infill
        if infill is None:
            self.infillCheckBox.setEnabled(False)
            self.infillCheckBox.setCheckState(False)
        else:
            self.infillCheckBox.setEnabled(True)

    def getTAnalatical(self):
        useTan = True
        xTan = self.xTAnalaticalSpinBox.value()
        yTan = self.yTAnalaticalSpinBox.value()
        return useTan, xTan, yTan

    def setSoilProperties(self, build=None):
        if not build:
            build = self.current_building()
        xrf = build.soil_reflection_prop_x
        yrf = build.soil_reflection_prop_y
        soilProp = [build.soilType, xrf.T0, xrf.Ts, xrf.S, xrf.S0]
        xSoilProp = [xrf.B1, xrf.N, build.Bx]
        ySoilProp = [yrf.B1, yrf.N, build.By]
        for row, item in enumerate(soilProp):
            if row == 0:
                item = QTableWidgetItem("%s " % item)
            else:
                item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.soilPropertiesTable.setItem(row, 0, item)

        for row, item in enumerate(xSoilProp):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.soilPropertiesTable.setItem(row + len(soilProp), 0, item)

        for row, item in enumerate(ySoilProp):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.soilPropertiesTable.setItem(row + len(soilProp), 1, item)

    def updateBCurve(self, build):
        self.p.clear()
        self.p.addLegend()
        self.p.legend.anchor((-9, 0), (0, 0))
        self.p.setTitle('منحنی ضریب بازتاب، خاک نوع {0}، پهنه با خطر نسبی {1}'.format(
            build.soilType, build.risk_level))
        penB1 = pg.mkPen('r', width=2, style=Qt.DashLine)
        penN = pg.mkPen('g', width=2)
        penB = pg.mkPen('b', width=3)
        penTx = pg.mkPen((153, 0, 153), width=1, style=Qt.DashDotLine)
        penTy = pg.mkPen((153, 0, 0), width=1, style=Qt.DashDotDotLine)
        dt = build.soil_reflection_prop_x.dt
        B1 = build.soil_reflection_prop_x.b1Curve
        N = build.soil_reflection_prop_x.nCurve
        B = build.soil_reflection_prop_x.bCurve
        x = np.arange(0, 4.5, dt)
        self.p.plot(x, B1, pen=penB1, name="B1", clear=True)
        self.p.plot(x, N, pen=penN, name="N")
        self.p.plot(x, B, pen=penB, name="B")
        self.p.addLine(x=build.Tx, pen=penTx)
        self.p.addLine(x=build.Ty, pen=penTy)
        Tx, Ty = build.Tx, build.Ty
        THtml = 'T<sub>{0}</sub> = {1:.2f}'
        TxHtml, TyHtml = THtml.format('x', Tx), THtml.format('y', Ty)
        text = pg.TextItem(html=TxHtml, anchor=(0, 1.5), border='k', fill=(0, 0, 255, 100))
        self.p.addItem(text)
        text.setPos(Tx, B.max())
        text = pg.TextItem(html=TyHtml, anchor=(0, 3), border='k', fill=(0, 0, 255, 100))
        self.p.addItem(text)
        text.setPos(Ty, B.max())
        self.p.setYRange(0, B.max() + 1, padding=0)

    def current_building(self):
        risk_level = self.accText.text()
        city = self.get_current_shahr()
        height = self.HSpinBox.value()
        importance_factor = float(self.IBox.currentText())
        soil = self.get_current_soil_type()
        noStory = self.storySpinBox.value()
        x_system = self.xactivate()
        y_system = self.yactivate()
        if not x_system and y_system:
            return None
        xSystemType, xLateralType = x_system[0], x_system[1]
        ySystemType, yLateralType = y_system[0], y_system[1]
        xSystem = StructureSystem(xSystemType, xLateralType, "X")
        ySystem = StructureSystem(ySystemType, yLateralType, "Y")
        self.setInfillCheckBoxStatus(xSystem, ySystem)
        Tan = self.getTAnalatical()
        useTan = Tan[0]
        xTan = Tan[1]
        yTan = Tan[2]
        is_infill = self.infillCheckBox.isChecked()
        build = Building(risk_level, importance_factor, soil, noStory, height, is_infill,
                         xSystem, ySystem, city, xTan, yTan, useTan)
        return build

    def calculate(self):
        self.dirty = False
        self.final_building = self.current_building()
        if not self.final_building:
            return
        self.setSoilProperties(self.final_building)
        self.structure_model.beginResetModel()
        self.structure_model.build = self.final_building
        self.structure_model.endResetModel()
        self.resizeColumns()
        results = self.final_building.results
        if results[0] is True:
            Cx, Cy = results[1], results[2]
            resultStrx = '<font size=6 color=blue>C<sub>x</sub> = %.4f , K<sub>x</sub> = %.2f</font>' % (Cx, self.final_building.kx)
            resultStrx_drift = '<font size=6 color=blue>C<sub>xdrift</sub> = %.4f , K<sub>xdrift</sub> = %.2f</font>' % (
                self.final_building.results_drift[1], self.final_building.kx_drift)
            resultStry = '<font size=6 color=blue>C<sub>y</sub> = %.4f , K<sub>x</sub> = %.2f</font>' % (Cy, self.final_building.ky)
            resultStry_drift = '<font size=6 color=blue>C<sub>ydrift</sub> = %.4f , K<sub>ydrift</sub> = %.2f</font>' % (
                self.final_building.results_drift[2], self.final_building.ky_drift)
            # self.updateBCurve(self.final_building)
            self.dirty = True
            # self.action_to_etabs.setEnabled(True)
            # self.action_word.setEnabled(True)
            # self.action_save.setEnabled(True)

        else:
            # self.action_to_etabs.setEnabled(False)
            # self.action_word.setEnabled(False)
            # self.action_save.setEnabled(False)
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, str(err))
            return

    def export_to_word(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.final_building)
        export_result.to_word()

    def save(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, None)
        export_result.to_json()

    def load(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'load project',
                                                  self.lastDirectory, "json(*.json)")
        if filename == '':
            return
        config.load(self, filename)
        self.calculate()

    def exportBCurveToImage(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_image()

    def exportBCurveToCsv(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_csv()

