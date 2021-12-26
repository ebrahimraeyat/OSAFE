
from pathlib import Path

from PySide2 import QtCore


class CivilScaleResponseSpec:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_scale_response_spec",
            "Response Spec.")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_scale_response_spec",
            "Scale Response Spectrum Analysis")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "balance.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from civilTools.gui_civiltools.gui_check_legal import (
            allowed_to_continue,
            show_warning_about_number_of_use
        )
        allow, check = allowed_to_continue(
            'response_spectrum.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/2370d564be6b4ba2508f8314a3358970/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from civilTools.py_widget import response_spectrum
        import FreeCADGui as Gui
        win = response_spectrum.Form(etabs)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

        