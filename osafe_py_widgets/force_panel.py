from pathlib import Path

from PySide2.QtWidgets import QMessageBox
import FreeCAD
import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent


class ForceTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'force_panel.ui'))
        self.foun = FreeCAD.ActiveDocument.Foundation
        self.fill_load_cases()
        self.create_connections()
        self.all_loads = []
        self.hide_loads()

    def create_connections(self):
        self.form.assign_button.clicked.connect(self.assign_load)
        self.form.loadcase.currentIndexChanged.connect(self.hide_loads)
    
    def fill_load_cases(self):
        deads = []
        try:
            import find_etabs
            etabs, _ = find_etabs.find_etabs(run=False)
            deads = etabs.load_patterns.get_special_load_pattern_names(1)
        except:
            if hasattr(FreeCAD, 'load_cases'):
                deads = FreeCAD.load_cases
        self.form.loadcase.addItems(deads)

    def hide_loads(self):
        try:
            loads = FreeCAD.ActiveDocument.findObjects(Type='Fem::ConstraintForce')
            for load in loads:
                load.ViewObject.hide()
            self.all_loads = [load.Name for load in loads]
        except TypeError:
            pass

    def assign_load(self):
        loadcase = self.form.loadcase.currentText()
        if not loadcase:
            QMessageBox.warning(None,
                'Dead load case',
                'Please Select Dead loadcase first.',
                )
            return
        load_value = self.form.load_value.value()
        version = float('.'.join(FreeCAD.Version()[0:2]))
        if version <= 0.19:
            Gui.activateWorkbench("FemWorkbench")
            Gui.activateWorkbench("OSAFEWorkbench")
        loads = FreeCAD.ActiveDocument.findObjects(Type='Fem::ConstraintForce')
        all_loads = [load.Name for load in loads]
        if loadcase in all_loads:
            load = FreeCAD.ActiveDocument.getObject(loadcase)
            load.Force = load_value
            load.ViewObject.show()
        else:
            constraint = FreeCAD.ActiveDocument.addObject('Fem::ConstraintForce', loadcase)
            constraint.addProperty('App::PropertyString', 'loadcase', 'Base')
            constraint.loadcase = loadcase
            references_names = []
            top_of_foundation = self.foun.Shape.BoundBox.ZMax
            for i, face in enumerate(self.foun.Shape.Faces, start=1):
                if face.BoundBox.ZMin == top_of_foundation:
                    references_names.append(f'Face{i}')
            constraint.References =  [(self.foun, tuple(references_names))]
            constraint.Force = load_value
            constraint.Reversed = True
        FreeCAD.ActiveDocument.recompute()
        
if __name__ == '__main__':
    panel = ForceTaskPanel()
