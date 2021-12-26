
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilShowTorsion:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_torsion",
            "Torsion")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_torsion",
            "Get Torsion of Structure")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "torsion.svg"
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
            'torsion.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/d1591790a52a62b3e66bb70f45738105/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from civilTools.py_widget import torsion
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        win = torsion.Form(etabs)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        