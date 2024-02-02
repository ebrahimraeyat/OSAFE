from pathlib import Path


import FreeCAD
import FreeCADGui as Gui

from osafe_py_widgets import resource_rc
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt

punch_path = Path(__file__).parent.parent


class EtabsTaskPanel:

    def __init__(
        self,
        etabs,
        ):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'etabs_panel.ui'))
        self.etabs = etabs
        # self.set_foundation_level()
        self.update_gui()
        self.create_connections()

    def create_new_document(self):
        name = self.etabs.get_file_name_without_suffix()
        FreeCAD.newDocument(name)

    def update_gui(self):
        self.set_load_cases()
        self.fill_levels()
        self.set_filename()

    def set_load_cases(self):
        FreeCAD.load_cases = self.etabs.load_cases.get_load_cases()
        FreeCAD.dead = self.etabs.load_patterns.get_special_load_pattern_names(1)

    def fill_levels(self):
        self.form.levels_list.clear()
        levels_names = self.etabs.story.get_level_names()
        self.form.levels_list.addItems(levels_names[1:])
        lw = self.form.levels_list
        for i in range(lw.count()):
            item = lw.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if i == 0:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def set_filename(self):
        filename = Path(self.etabs.SapModel.GetModelFilename()).with_suffix('.F2k')
        self.form.filename.setText(str(filename))
        
    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.import_data.clicked.connect(self.import_data)
        self.form.help.clicked.connect(self.show_help)
        self.form.cancel_pushbutton.clicked.connect(self.accept)
        self.form.all_beams.clicked.connect(self.selection_changed)
        self.form.selected_beams.clicked.connect(self.selection_changed)
        self.form.exclude_selected_beams.clicked.connect(self.selection_changed)

    def selection_changed(self):
        self.form.levels_list.setEnabled(not self.form.selected_beams.isChecked())

    def set_foundation_level(self):
        self.etabs.set_current_unit('KN', 'm')
        base_level = self.etabs.story.get_base_name_and_level()[1]
        self.form.foundation_level.setValue(base_level)

    def browse(self):
        ext = '.f2k'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)

    def import_data(self):
        self.etabs.set_current_unit('KN', 'mm')
        selected_beam_names = self.etabs.select_obj.get_selected_obj_type(2)
        selected_beam_names = [name for name in selected_beam_names if self.etabs.frame_obj.is_beam(name)]
        self.create_new_document()
        self.top_of_foundation = self.form.foundation_level.value() * 1000
        self.add_load_combinations_names()
        self.import_beams_columns(selected_beam_names)
        self.create_f2k()
        Gui.Control.closeDialog()
        Gui.Selection.clearSelection()

    def getStandardButtons(self):
        return 0

    def accept(self):
        Gui.Control.closeDialog()

    def import_beams_columns(self,
            selected_beam_names: list,
            ):
        from osafe_py_widgets import etabs_punch
        import_beams = self.form.beams_group.isChecked()
        beams_names = None
        elevations = []
        if import_beams:
            level_names = []
            lw = self.form.levels_list
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    level_name = item.text()
                    level_names.append(level_name)
                    elevations.append(self.etabs.SapModel.Story.GetElevation(level_name)[0])
            selected_beams = self.form.selected_beams.isChecked()
            exclude_selected_beams = self.form.exclude_selected_beams.isChecked()
            #  types: {1: steel, 2: concrete, 3: composite Beam, 7: No Design, 13: composite column }
            beams, _ = self.etabs.frame_obj.get_beams_columns(stories=level_names, types=[1,2,3,7,13])
            beams = self.etabs.frame_obj.get_unique_frames(beams)
            if self.form.all_beams.isChecked():
                beams_names = beams
            elif selected_beams:
                beams_names = selected_beam_names
            elif exclude_selected_beams:
                beams_names = set(beams).difference(selected_beam_names)
            beams_names = self.etabs.frame_obj.get_unique_frames(beams_names)
        punch = etabs_punch.EtabsPunch(
                etabs_model = self.etabs,
                beam_names = beams_names,
                top_of_foundation=self.top_of_foundation,
            )
        punch.import_data(
            import_beams=import_beams,
            beam_elevations=elevations,
            )

    def create_f2k(self):
        filename = self.form.filename.text()
        filename_path = Path(filename)
        name = f"{filename_path.name.rstrip(filename_path.suffix)}_export{filename_path.suffix}"
        output_filename = str(filename_path.with_name(name))
        from osafe_objects.f2k_object import make_safe_f2k
        make_safe_f2k(filename, output_filename)
        if self.form.f2k_groupbox.isChecked():
            import create_f2k
            writer = create_f2k.CreateF2kFile(
                    filename_path,
                    self.etabs,
                    model_datum=self.top_of_foundation,
                    )
            pixmap = QPixmap(str(punch_path / 'osafe_images' / 'tick.svg'))
            d = {
                1 : self.form.one,
                2 : self.form.two,
                3 : self.form.three,
                4 : self.form.four,
                5 : self.form.five,
            }
            for ret in writer.create_f2k():
                if type(ret) == tuple and len(ret) == 3:
                    message, percent, number = ret
                    if type(message) == str and type(percent) == int:
                        self.form.result_label.setText(message)
                        self.form.progressbar.setValue(percent)
                        if number < 6:
                            d[number].setPixmap(pixmap)
                elif type(ret) == bool:
                    if not ret:
                        self.form.result_label.setText("Error Occurred, process did not finished.")
                    self.form.start_button.setEnabled(False)
                elif type(ret) == str:
                    self.form.result_label.setText(ret)

    def add_load_combinations_names(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return
        d = {}
        all_load_combos = self.etabs.load_combinations.get_load_combination_names()
        all_load_combos_string = ' '.join(all_load_combos)
        d['all_load_combinations'] = all_load_combos_string
        types = ['concrete', 'steel']
        type_combos = self.etabs.database.select_design_load_combinations(types=types)
        for type_, combos in type_combos.items():
            if combos is None:
                combos = []
            load_combos_string = ','.join(combos)
            d[f'{type_}_load_combinations'] = load_combos_string
        doc.Meta = d
        
    def show_help(self):
        from freecad_funcs import show_help
        show_help('import_model.html', 'OSAFE')
 
if __name__ == '__main__':
    panel = EtabsTaskPanel()
