
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
                   Path(__file__).parent.parent / "osafe_images" / "dxf.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        from osafe_py_widgets.export import export_to_dxf_dialog
        win = export_to_dxf_dialog.Form()
        Gui.Control.showDialog(win)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OsafeImportDxf:
    """Gui command for import DXF files."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "OSAFE",
            "Import DXF")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "OSAFE",
            "Import DXF file into current model")
        path = str(
                   Path(__file__).parent.parent / "osafe_images" / "import_dxf.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        from osafe_py_widgets.export import import_from_dxf_dialog
        win = import_from_dxf_dialog.Form()
        Gui.Control.showDialog(win)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None