import sys
from pathlib import Path

from PySide2 import QtCore

from PySide2 import uic
from PySide2.QtCore import Qt

cfactor_path = Path(__file__).absolute().parent.parent

beamj_base, beamj_window = uic.loadUiType(cfactor_path / 'widgets' / 'beam_j.ui')

class BeamJForm(beamj_base, beamj_window):
    def __init__(self,
            etabs_model,
            table_model,
            parent=None):
        super(BeamJForm, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.table_model = table_model
        self.create_connections()

    def accept(self):
        load_combinations = None
        selected_beams = self.selected_beams.isChecked()
        exclude_selected_beams = self.exclude_selected_beams.isChecked()
        beams_names = None
        if (selected_beams or exclude_selected_beams):
            beams, _  = self.etabs.frame_obj.get_beams_columns()
            names = self.etabs.select_obj.get_selected_obj_type(2)
            names = [name for name in names if self.etabs.frame_obj.is_beam(name)]
            if selected_beams:
                beams_names = set(names).intersection(beams)
            elif exclude_selected_beams:
                beams_names = set(beams).difference(names)
        phi = self.phi_spinbox.value()
        num_iteration = self.iteration_spinbox.value()
        tolerance = self.tolerance_spinbox.value()
        j_max_value = self.maxj_spinbox.value()
        j_min_value = self.minj_spinbox.value()
        initial_j = self.initial_checkbox.isChecked()
        initial_j = self.initial_spinbox.value() if initial_j else None
        decimals = self.rounding.isChecked()
        decimals = self.round_decimals.value() if decimals else None
        df = self.etabs.frame_obj.correct_torsion_stiffness_factor(
            load_combinations,
            beams_names,
            phi,
            num_iteration,
            tolerance,
            j_max_value,
            j_min_value,
            initial_j,
            decimals,
            )
        super(BeamJForm, self).accept()
        self.table_model.show_results(df, None, self.table_model.BeamsJModel, self.etabs.view.show_frame)

    def create_connections(self):
        self.initial_checkbox.stateChanged.connect(self.set_initial_j)

    def set_initial_j(self):
        if self.initial_checkbox.isChecked():
            self.initial_spinbox.setEnabled(True)
        else:
            self.initial_spinbox.setEnabled(False)

