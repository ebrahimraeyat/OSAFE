
from pathlib import Path

from PySide2 import QtCore

import FreeCAD
import FreeCADGui as Gui


class OsafeExportStrips:
    """Gui command for the Create DXF."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "OSAFE",
            "Export Strips")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "OSAFE",
            "Export Strips to ETABS or SAFE")
        path = str(
                   Path(__file__).parent.parent / "osafe_images" / "export_strips.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        from osafe_py_widgets.export import export_strips_panel
        win = export_strips_panel.Form()
        Gui.Control.showDialog(win)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


if FreeCAD.GuiUp:
    Gui.addCommand('osafe_export_strips',OsafeExportStrips())