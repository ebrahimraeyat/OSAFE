
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilCreatePeriodFile:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_period",
            "create period file")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_perion",
            "Create Period File")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "time.svg"
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
        tx, ty, _ = etabs.get_drift_periods()
        
    def IsActive(self):
        return True


        