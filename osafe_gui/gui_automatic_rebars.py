
from pathlib import Path

from PySide import QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui


class OsafeAutomaticRebar:
    """Gui command for the creating stirp automatically in mat foundations."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "osafe",
            "Auto Rebar")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "osafe",
            "Create Rebars automatically from strips")
        path = str(
                   Path(__file__).parent.parent / "osafe_images" / "osafe_rebar.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        from osafe_py_widgets import draw_automatic_rebars
        win = draw_automatic_rebars.Form()
        Gui.Control.showDialog(win)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

if FreeCAD.GuiUp:
    Gui.addCommand('osafe_automatic_rebars', OsafeAutomaticRebar())