
from pathlib import Path

from PySide2 import QtCore

import FreeCAD
import FreeCADGui as Gui


class OsafeDxf:
    """Gui command for the Create DXF."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "OSAFE",
            "DXF")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "OSAFE",
            "Export Foundation To DXF")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "dxf.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        from safe.punch.py_widget.export import export_to_dxf_dialog
        win = export_to_dxf_dialog.Form()
        Gui.Control.showDialog(win)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None