from pathlib import Path

import FreeCAD
import FreeCADGui as Gui
from safe.punch import punch_funcs

punch_path = Path(__file__).parent.parent



class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'foundation_panel.ui'))
        self.fill_height()

    def fill_height(self):
        try:
            import FreeCAD
            doc = FreeCAD.ActiveDocument
            base = doc.BaseFoundation
            height = base.height.Value
            self.form.height_spinbox.setValue(int(height / 10))
        except:
            pass

    def accept(self):
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
        if self.form.selection_only.isChecked():
            sel = Gui.Selection.getSelection()
            if sel:
                for o in sel:
                    if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
                        base_foundations.append(o)
        if not base_foundations:
            for o in FreeCAD.ActiveDocument.Objects:
                if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
                    base_foundations.append(o)
        from safe.punch.etabs_foundation import make_foundation
        make_foundation(
            cover=cover,
            fc=fc,
            height= height,
            foundation_type=foundation_type,
            continuous_layer=continuous_layer,
            base_foundations=base_foundations,
            ks=ks,
            )
        # Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
        Gui.Control.closeDialog()
