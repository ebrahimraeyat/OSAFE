
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilStoryForces:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_forces",
            "Story Forces")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_forces",
            "Show Stories Forces")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "shear.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        data, headers = etabs.get_story_forces_with_percentages()
        table_model.show_results(data, headers, table_model.StoryForcesModel)
        
    def IsActive(self):
        return True


        