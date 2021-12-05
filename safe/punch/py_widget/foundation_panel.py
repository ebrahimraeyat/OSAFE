from pathlib import Path

import FreeCADGui as Gui

punch_path = Path(__file__).parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'foundation_panel.ui'))

    def accept(self):
        cover = self.form.cover.value() * 10
        fc = self.form.fc.value()
        height = self.form.height_spinbox.value() * 10
        continuous_layer = self.form.continuous_layer.currentText()
        if self.form.mat.isChecked():
            foundation_type = 'Mat'
        elif self.form.strip.isChecked():
            foundation_type = 'Strip'
        from safe.punch.etabs_foundation import make_foundation
        make_foundation(
            cover=cover,
            fc=fc,
            height= height,
            foundation_type=foundation_type,
            continuous_layer=continuous_layer,
            )
        Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
        Gui.Control.closeDialog()
