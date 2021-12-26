
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilBeamJ:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_beam_j",
            "Beam j")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_beam_j",
            "Modify Torsion Stiffness of Concrete Beams")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "beam_j_torsion.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        from civilTools.gui_civiltools.gui_check_legal import (
                allowed_to_continue,
                show_warning_about_number_of_use,
                )
        allow, check = allowed_to_continue(
            'correct_j.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/98b4863d25f0779dce2347d73a99212b/raw',
            'cfactor',
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from civilTools.py_widget import beam_j
        win = beam_j.Form(etabs)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        