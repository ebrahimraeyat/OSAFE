from pathlib import Path

import FreeCAD
import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent


class ForceTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'force_panel.ui'))
        self.create_connections()

    def create_connections(self):
        self.form.assign_button.clicked.connect(self.assign_load)

    def assign_load(self):
        loadcase = self.form.loadcase.currentText()
        load_value = self.form.load_value.value()
        foun = FreeCAD.ActiveDocument.Foundation
        constraint = FreeCAD.ActiveDocument.addObject('Fem::ConstraintForce', 'Force')
        constraint.addProperty('App::PropertyString', 'loadcase', 'Base')
        constraint.loadcase = loadcase
        constraint.References =  [(foun, foun.top_face)]
        constraint.Force = load_value
        constraint.Reversed = True
        
if __name__ == '__main__':
    panel = ForceTaskPanel()
