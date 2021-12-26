from pathlib import Path

from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent


class Form(*loadUiType(str(civiltools_path / 'widgets' / 'response_spectrum.ui'))):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.setupUi(self)
        self.form = self
        self.etabs = etabs_obj
        self.fill_100_30_fields()
        self.select_spect_loadcases()
        self.create_connections()

    def create_connections(self):
        self.combination.clicked.connect(self.reset_widget)
        self.angular.clicked.connect(self.reset_widget)
        self.angular.clicked.connect(self.fill_angular_fields)

    def reset_widget(self):
        if self.combination.isChecked():
            self.angular_specs.setEnabled(False)
            self.section_cuts.setEnabled(False)
            self.x_loadcase_list.setEnabled(True)
            self.y_loadcase_list.setEnabled(True)
            self.y_scalefactor.setEnabled(True)
        elif self.angular.isChecked():
            self.angular_specs.setEnabled(True)
            self.section_cuts.setEnabled(True)
            self.x_loadcase_list.setEnabled(False)
            self.y_loadcase_list.setEnabled(False)
            self.y_scalefactor.setEnabled(False)

    def accept(self):
        ex_name = self.static_x.currentText()
        ey_name = self.static_y.currentText()
        x_specs = [item.text() for item in self.x_loadcase_list.selectedItems()]
        y_specs = [item.text() for item in self.y_loadcase_list.selectedItems()]
        angular_specs = [item.text() for item in self.angular_specs.selectedItems()]
        section_cuts = [item.text() for item in self.section_cuts.selectedItems()]
        x_scale_factor = self.x_scalefactor.value()
        y_scale_factor = self.y_scalefactor.value()
        num_iteration = self.iteration.value()
        tolerance = self.tolerance.value()
        reset = self.reset.isChecked()
        analyze = self.analyze.isChecked()
        if self.angular.isChecked():
            self.etabs.angles_response_spectrums_analysis(
                ex_name,
                ey_name,
                angular_specs,
                section_cuts,
                x_scale_factor,
                num_iteration,
                tolerance,
                reset,
                analyze,
            )
        else:
            self.etabs.scale_response_spectrums(
                ex_name,
                ey_name,
                x_specs,
                y_specs,
                x_scale_factor,
                y_scale_factor,
                num_iteration,
                tolerance,
                reset,
                analyze,
            )
        msg = "Done Response Spectrum Analysis."
        QMessageBox.information(None, 'Successful', str(msg))

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    def select_spect_loadcases(self):
        for lw in (self.x_loadcase_list, self.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)
    
    def select_angular_list(self):
        for lw in (self.angular_specs, self.section_cuts):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)

    def fill_100_30_fields(self):
        ex_name, ey_name = self.etabs.load_patterns.get_EX_EY_load_pattern()
        x_names, y_names = self.etabs.load_patterns.get_load_patterns_in_XYdirection()
        self.static_x.addItems(x_names)
        self.static_y.addItems(y_names)
        if ex_name is not None:
            self.static_x.setCurrentText(ex_name)
        if ey_name is not None:
            self.static_y.setCurrentText(ey_name)
        x_specs, y_specs = self.etabs.load_cases.get_response_spectrum_xy_loadcases_names()
        self.x_loadcase_list.addItems(x_specs)
        self.y_loadcase_list.addItems(y_specs)

    def fill_angular_fields(self):
        section_cuts_angles = self.etabs.database.get_section_cuts_angle()
        angles = list(section_cuts_angles.values())
        section_cuts = list(section_cuts_angles.keys())
        angles_spectral = self.etabs.load_cases.get_spectral_with_angles(angles)
        specs = list(angles_spectral.values())
        self.angular_specs.addItems(specs)
        self.section_cuts.addItems(section_cuts)
        self.select_angular_list()
