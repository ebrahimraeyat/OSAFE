
from pathlib import Path

import PySide2
from PySide2 import QtCore


# import FreeCAD
import FreeCADGui as Gui



class CivilExplodLoadPatterns:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_explode",
            "Explode Load Patterns")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_explode",
            "Explode Load Patterns")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "explode.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        def get_mdiarea():
            """ Return FreeCAD MdiArea. """
            mw = Gui.getMainWindow()
            if not mw:
                return None
            childs = mw.children()
            for c in childs:
                if isinstance(c, PySide2.QtWidgets.QMdiArea):
                    return c
            return None

        mdi = get_mdiarea()
        if not mdi:
            return None
        from civilTools.gui_civiltools.gui_check_legal import (
                allowed_to_continue,
                show_warning_about_number_of_use,
                )
        allow, check = allowed_to_continue(
            'explode_loads.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/f05421c70967b698ca9016a1bdb54b01/raw',
            'cfactor',
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        from civilTools.py_widget import explode_seismic_load_patterns
        etabs = etabs_obj.EtabsModel()
        panel = explode_seismic_load_patterns.Form(etabs)
        Gui.Control.showDialog(panel)
        # sub = mdi.addSubWindow(panel)
        # sub.show()
        # Gui.Control.closeDialog()

        show_warning_about_number_of_use(check)
        # return panel
        
    def IsActive(self):
        return True


        