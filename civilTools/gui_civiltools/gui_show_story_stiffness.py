
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilShowStoryStiffness:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_stiffness",
            "Story stiffness")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_stiffness",
            "Show Stories Stiffness")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "show_stiffness.svg"
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
        from civilTools.py_widget import show_siffness_story_way
        win = show_siffness_story_way.Form(etabs)
        e_name = etabs.get_file_name_without_suffix()
        way_radio_button = {'2800': win.radio_button_2800,
                            'modal': win.radio_button_modal,
                            'earthquake': win.radio_button_earthquake}
        for w, rb in way_radio_button.items():
            name = f'{e_name}_story_stiffness_{w}_table.json'
            json_file = Path(etabs.SapModel.GetModelFilepath()) / name
            if not json_file.exists():
                rb.setChecked(False)
                rb.setEnabled(False)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        