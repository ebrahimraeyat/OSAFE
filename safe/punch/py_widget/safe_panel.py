from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent



class Safe12TaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'safe_panel.ui'))
        self.create_connections()
        self.fill_f2k_filename()

    def create_connections(self):
        self.form.export_button.clicked.connect(self.export_to_safe)
        self.form.browse_input.clicked.connect(self.openf2k)
        self.form.browse_output.clicked.connect(self.savef2k)

    def fill_f2k_filename(self):
        if FreeCAD.ActiveDocument:
            foun = FreeCAD.ActiveDocument.Foundation
            if foun and hasattr(foun, 'F2K'):
                self.form.input_f2k.setText(foun.F2K)
                filename = Path(foun.F2K)
                name = f"{filename.name.rstrip(filename.suffix)}_export{filename.suffix}"
                filename = filename.with_name(name)
                self.form.output_f2k.setText(str(filename))

    def openf2k(self):
        ext = '.f2k'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                            None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.input_f2k.setText(filename)
    
    def savef2k(self):
        ext = '.f2k'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                            None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.output_f2k.setText(filename)

    def export_to_safe(self):
        software = self.form.software.currentText()
        split = self.form.split.isChecked()
        is_slabs = self.form.slabs_checkbox.isChecked()
        is_area_loads = self.form.loads_checkbox.isChecked()
        is_openings = self.form.openings_checkbox.isChecked()
        is_strips = self.form.strips_checkbox.isChecked()
        is_stiffs = self.form.stiff_elements_checkbox.isChecked()
        is_punches = self.form.punches.isChecked()
        soil_name = self.form.soil_name.text()
        soil_modulus = self.form.soil_modulus.value()
        doc = FreeCAD.ActiveDocument
        slab_names = []
        software_name = software.split()[0]
        if software in ('SAFE 20', 'ETABS 19'):
            from etabs_api import etabs_obj
            etabs = etabs_obj.EtabsModel(backup=False, software=software_name)
            etabs.unlock_model()
            if is_slabs:
                slab_names = etabs.area.export_freecad_slabs(
                    doc,
                    split_mat = split,
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
                etabs.area.create_punching_shear_general_table(punches)
                etabs.area.create_punching_shear_perimeter_table(punches)
            etabs.SapModel.View.RefreshView()
        elif software == 'SAFE 16':
            from safe.punch.safe_read_write_f2k import FreecadReadwriteModel as FRW
            input_f2k_path = self.form.input_f2k.text()
            output_f2k_path = self.form.output_f2k.text()
            rw = FRW(input_f2k_path, output_f2k_path, doc)
            if is_slabs:
                slab_names = rw.export_freecad_slabs(
                    split_mat = split,
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
            if self.form.wall_loads.isChecked():
                rw.export_freecad_wall_loads()
            if is_openings:
                rw.export_freecad_openings(doc)
            if is_strips:
                if doc.Foundation.foundation_type == 'Strip':
                    rw.export_freecad_strips()
            if is_stiffs:
                rw.export_freecad_stiff_elements()
            if is_punches:
                rw.export_punch_props()
            rw.safe.write()
        Gui.Control.closeDialog()

if __name__ == '__main__':
    panel = SafeTaskPanel()
