from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent


class ForceTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'force_panel.ui'))
        self.foun = FreeCAD.ActiveDocument.Foundation
        self.form.loadcase.addItems(self.foun.loadcases)
        self.create_connections()
        self.all_loads = []
        self.hide_loads()

    def create_connections(self):
        self.form.assign_button.clicked.connect(self.assign_load)
        self.form.loadcase.currentIndexChanged.connect(self.hide_loads)

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
        load_value = self.form.load_value.value()
        if loadcase in self.all_loads:
            load = FreeCAD.ActiveDocument.getObject(loadcase)
            load.Force = load_value
            load.ViewObject.show()
        else:
            constraint = FreeCAD.ActiveDocument.addObject('Fem::ConstraintForce', loadcase)
            constraint.addProperty('App::PropertyString', 'loadcase', 'Base')
            constraint.loadcase = loadcase
            constraint.References =  [(self.foun, self.foun.top_face)]
            constraint.Force = load_value
            constraint.Reversed = True
        FreeCAD.ActiveDocument.recompute()
        
if __name__ == '__main__':
    panel = ForceTaskPanel()
