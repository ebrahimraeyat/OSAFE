
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilShowWeakness:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_weakness",
            "Weakness")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_weakness",
            "Show Weakness Tables")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "show_weakness.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from civilTools.py_widget import show_weakness
        win = show_weakness.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        