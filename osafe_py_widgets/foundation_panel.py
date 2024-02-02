from pathlib import Path

from PySide2.QtWidgets import QMessageBox

import FreeCAD
import FreeCADGui as Gui
from osafe_py_widgets import resource_rc

punch_path = Path(__file__).parent.parent



class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'foundation_panel.ui'))
        self.create_connections()
        self.fill_height()
        self.update_gui()

    def getStandardButtons(self):
        return 0

    def create_connections(self):
        self.form.strip.clicked.connect(self.update_gui)
        self.form.mat.clicked.connect(self.update_gui)
        self.form.create_pushbutton.clicked.connect(self.create)
        self.form.cancel_pushbutton.clicked.connect(self.accept)

    def update_gui(self):
        if self.form.strip.isChecked():
            self.form.ks.setEnabled(False)
            self.form.continuous_layer.setEnabled(True)
        elif self.form.mat.isChecked():
            self.form.ks.setEnabled(True)
            self.form.continuous_layer.setEnabled(False)

    def fill_height(self):
        try:
            import FreeCAD
            doc = FreeCAD.ActiveDocument
            base = doc.BaseFoundation
            height = base.height.Value
            self.form.height_spinbox.setValue(int(height / 10))
        except:
            pass

    def create(self):
        cover = self.form.cover.value() * 10
        fc = self.form.fc.value()
        ks = self.form.ks.value()
        height = self.form.height_spinbox.value() * 10
        continuous_layer = self.form.continuous_layer.currentText()
        if self.form.mat.isChecked():
            foundation_type = 'Mat'
        elif self.form.strip.isChecked():
            foundation_type = 'Strip'
        base_foundations = []
        openings = []
        if self.form.selection_only.isChecked():
            sel = Gui.Selection.getSelection()
            if sel:
                for o in sel:
                    if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
                        base_foundations.append(o)
                    elif hasattr(o, "IfcType") and o.IfcType == "Opening Element":
                        openings.append(o)
        if not base_foundations:
            for o in FreeCAD.ActiveDocument.Objects:
                if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
                    base_foundations.append(o)
                elif hasattr(o, "IfcType") and o.IfcType == "Opening Element":
                    openings.append(o)
        if len(base_foundations) == 0:
            if QMessageBox.question(
                None,
                'Base Foundation',
                'There is no Base Foundation in your model, Do you want to draw those?',
                ) == QMessageBox.Yes:
                Gui.Control.closeDialog()
                Gui.runCommand("automatic_base_foundation") 
            return
        from osafe_objects.etabs_foundation import make_foundation
        make_foundation(
            cover=cover,
            fc=fc,
            height= height,
            foundation_type=foundation_type,
            continuous_layer=continuous_layer,
            base_foundations=base_foundations,
            ks=ks,
            openings=openings,
            )
        # Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
        Gui.Control.closeDialog()

    def accept(self):
        Gui.Control.closeDialog()
