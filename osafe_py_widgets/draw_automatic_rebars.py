from pathlib import Path

from PySide.QtGui import QMessageBox

import FreeCAD
import FreeCADGui as Gui
from draftutils.translate import translate


from osafe_py_widgets import resource_rc

punch_path = Path(__file__).parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'draw_automatic_rebars.ui'))
        self.create_connections()
        # if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetBool("osafe_split_strips", False):
        #     self.form.split.setChecked(True)
        #     self.split_clicked(True)
        # tol = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetFloat("osafe_split_strips_tolerance", .001)
        # self.form.tolerance.setValue(tol)

    def create_connections(self):
        self.form.create_pushbutton.clicked.connect(self.create)
        self.form.cancel_pushbutton.clicked.connect(self.accept)
        self.form.help.clicked.connect(self.show_help)

    def create(self):
        doc = FreeCAD.ActiveDocument
        FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Automatic Rebars"))
        rebars = []
        for obj in doc.Objects:
            if (
                isinstance(obj, FreeCAD.DocumentObjectGroup) and
                'rebars' in obj.Label.lower()
            ):
                rebars.append(obj)
        if rebars and QMessageBox.question(
            None,
            'Remove Rebars',
            'There is rebars exists in Model, Do you want to remove those?',
            ) == QMessageBox.Yes:
            for rebar in rebars:
                for o in rebar.Group:
                    FreeCAD.ActiveDocument.removeObject(o.Name)
                FreeCAD.ActiveDocument.removeObject(rebar.Name)

        from osafe_objects import osafe_rebar
        top_rebar_diameter = int(self.form.top_rebar_diameter_combobox.currentText())
        bot_rebar_diameter = int(self.form.bot_rebar_diameter_combobox.currentText())
        stirrup_diameter = int(self.form.stirrup_rebar_diameter_combobox.currentText())
        min_ratio_of_rebars = .0018 if self.form.impose_minimum_checkbox.isChecked() else 0
        osafe_rebar.make_rebars(
            top_rebar_diameter=top_rebar_diameter,
            bot_rebar_diameter=bot_rebar_diameter,
            stirrup_diameter=stirrup_diameter,
            min_ratio_of_rebars=min_ratio_of_rebars
            )
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.ActiveDocument.commitTransaction()
        self.accept()

    def show_help(self):
        from freecad_funcs import show_help
        show_help('make_auto_rebars.html', 'OSAFE')
    
    def accept(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0
