
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui


class OsafeAutomaticStrip:
    """Gui command for the creating stirp automatically in mat foundations."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "osafe",
            "Auto Strip")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "osafe",
            "Create Strips automatically in mat foundations")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "auto_strip.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        # def is_foundation_type(obj):
        #     if hasattr(obj, 'IfcType') and obj.IfcType == 'Footing':
        #         return True
        #     return False

        # doc = FreeCAD.ActiveDocument
        # sel = Gui.Selection.getSelection()
        # foun = None
        # if sel and is_foundation_type(sel[0]):
        #     foun = sel[0]
        # if foun is None:
        #     for o in doc.Objects:
        #         if is_foundation_type(o):
        #             foun = o
        #             break
        # if foun is None:
        #     return
        # print('ali')
        from safe.punch.py_widget import draw_automatic_strip
        win = draw_automatic_strip.Form()
        Gui.Control.showDialog(win)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None