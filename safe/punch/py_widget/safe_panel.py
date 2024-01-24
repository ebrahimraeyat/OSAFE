from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

from PySide2.QtWidgets import QMessageBox, QFileDialog

from safe.punch.py_widget import resource_rc

from freecad_funcs import add_to_clipboard

punch_path = Path(__file__).parent.parent



class Safe12TaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'safe_panel.ui'))
        self.form.input_browse.setObjectName("input_browse")
        self.form.output_browse.setObjectName("output_browse")
        self.set_filename()
        self.create_connections()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetBool("export_columns_to_safe", False):
            self.form.columns.setChecked(True)

    def create_connections(self):
        self.form.export_button.clicked.connect(self.export)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.input_browse.clicked.connect(self.input_browse)
        self.form.output_browse.clicked.connect(self.output_browse)

    def set_filename(self):
        doc = FreeCAD.ActiveDocument
        if hasattr(doc, 'Safe'):
            f2k_file = doc.Safe
            filename_path = f2k_file.input
            self.form.input_filename.setText(filename_path)
            filename_path = f2k_file.output
            self.form.output_filename.setText(filename_path)

    def input_browse(self):
        ext = '.F2K'
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return False
        if not filename.upper().endswith(ext):
            filename += ext
        self.form.input_filename.setText(filename)
        doc = FreeCAD.ActiveDocument
        if hasattr(doc, 'Safe'):
            f2k_file = doc.Safe
            f2k_file.input = str(filename)
            doc.recompute([f2k_file])
        return True
    
    def output_browse(self):
        ext = '.F2K'
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return False
        if not filename.upper().endswith(ext):
            filename += ext
        self.form.output_filename.setText(filename)
        doc = FreeCAD.ActiveDocument
        if hasattr(doc, 'Safe'):
            f2k_file = doc.Safe
            f2k_file.output = str(filename)
            doc.recompute([f2k_file])
        return True

    def export(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return
        software = self.form.software.currentText()
        is_slabs = self.form.slabs_checkbox.isChecked()
        is_area_loads = self.form.loads_checkbox.isChecked()
        is_openings = self.form.openings_checkbox.isChecked()
        is_strips = self.form.strips_checkbox.isChecked()
        is_stiffs = self.form.stiff_elements_checkbox.isChecked()
        is_punches = self.form.punches.isChecked()
        is_columns = self.form.columns.isChecked()
        soil_name = self.form.soil_name.text()
        soil_modulus = self.form.soil_modulus.value()
        is_2d = 'Yes' if self.form.analysis_2d.isChecked() else 'No'
        max_mesh_size = self.form.max_mesh_size.value()
        slab_names = []
        software_name = software.split()[0]
        if software in ('SAFE 20', 'ETABS 19'):
            import etabs_obj
            etabs = etabs_obj.EtabsModel(backup=False, software=software_name)
            etabs.unlock_model()
            if is_slabs:
                slab_names = etabs.area.export_freecad_slabs(
                    doc,
                    soil_name=soil_name,
                    soil_modulus=soil_modulus,
                )
            if is_area_loads:
                try:
                    loads = doc.findObjects(Type='Fem::ConstraintForce')
                    for load in loads:
                        etabs.area.set_uniform_gravity_load(
                            slab_names,
                            load.loadcase,
                            load.Force,
                            )
                except TypeError:
                    print('Can not find any loads in model')
            if self.form.wall_loads.isChecked():
                etabs.area.export_freecad_wall_loads(doc)
            if is_openings:
                etabs.area.export_freecad_openings(doc)
            if is_strips:
                if doc.Foundation.foundation_type == 'Strip':
                    etabs.area.export_freecad_strips(doc)
            if is_stiffs:
                etabs.area.export_freecad_stiff_elements(doc)
            if is_punches:
                punches = []
                for o in doc.Objects:
                    if hasattr(o, "Proxy") and \
                        hasattr(o.Proxy, "Type") and \
                        o.Proxy.Type == "Punch":
                        punches.append(o)
                etabs.database.create_punching_shear_general_table(punches)
                etabs.database.create_punching_shear_perimeter_table(punches)
            etabs.SapModel.View.RefreshView()
        elif software == 'SAFE 16':
            if not hasattr(doc, 'Safe'):
                from safe.punch.f2k_object import make_safe_f2k
                make_safe_f2k('')
            input_f2k_path = self.form.input_filename.text()
            output_f2k_path = self.form.output_filename.text()
            f2k_file = doc.Safe
            f2k_file.input = str(input_f2k_path)
            f2k_file.output = str(output_f2k_path)
            doc.recompute([f2k_file])
            # check input f2k file
            from safe.punch.safe_read_write_f2k import get_f2k_version
            ver = get_f2k_version(doc=doc)
            if ver is None:
                QMessageBox.warning(None, "Missing Input F2k", "You don't have any input f2k file, Maybe the path is change. we try to find it!")
                if not f2k_file.input_str:
                    QMessageBox.warning(None, "Missing Input F2k", "You don't have any input f2k file, please select a valid path for input f2k.")
                    return False
                else:
                    import tempfile
                    default_tmp_dir = tempfile._get_default_tempdir()
                    name = next(tempfile._get_candidate_names())
                    punch_temp_file = Path(default_tmp_dir) / f'{name}.F2k'
                    with open(punch_temp_file, 'w') as f:
                        f.write(f2k_file.input_str)
                    f2k_file.input = str(punch_temp_file)
            elif ver < 14:
                QMessageBox.warning(None, "Version Error", f"The version of input f2k is {ver}, please convert it to version 14 or 16.")
                return 
            if output_f2k_path == '' or not Path(f2k_file.output).parent.exists():
                QMessageBox.warning(None, "Missing Output Path", "Your output folder for saving f2k file did not exists, please select a valid path for output f2k.")
                ret = self.form.output_browse.click()
                if not ret:
                    return
        
            from safe.punch.safe_read_write_f2k import FreecadReadwriteModel as FRW
            rw = FRW(f2k_file.input, f2k_file.output, doc)
            if is_slabs:
                slab_names = rw.export_freecad_slabs(
                    soil_name=soil_name,
                    soil_modulus=soil_modulus,
                )
                if is_area_loads:
                    try:
                        loads = doc.findObjects(Type='Fem::ConstraintForce')
                        for load in loads:
                            rw.add_uniform_gravity_load(
                                slab_names,
                                load.loadcase,
                                load.Force,
                                )
                    except TypeError:
                        print('Can not find any loads in model')
            rw.safe.set_analysis_type(is_2d=is_2d)
            rw.safe.set_mesh_options(mesh_size=max_mesh_size)
            if self.form.wall_loads.isChecked():
                rw.export_freecad_wall_loads()
            if is_openings:
                rw.export_freecad_openings(doc)
            if is_strips:
                rw.export_freecad_strips()
            if is_stiffs:
                rw.export_freecad_stiff_elements()
            if is_columns:
                rw.export_freecad_columns()
            if is_punches:
                rw.export_punch_props()
            rw.add_preferences()
            rw.safe.write()
            if Path(f2k_file.input).exists():
                with open(f2k_file.input) as f:
                    f2k_file.input_str = f.read()
        add_to_clipboard(f2k_file.output)
        Gui.Control.closeDialog()

    def reject(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0
    
if __name__ == '__main__':
    panel = Safe12TaskPanel()
