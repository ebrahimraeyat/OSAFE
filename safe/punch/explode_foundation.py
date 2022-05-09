from pathlib import Path
from PySide2 import QtCore
from PySide2.QtWidgets import  QMessageBox
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD

import FreeCADGui as Gui

from draftutils.messages import _msg, _err
from draftutils.translate import translate

from safe.punch.rectangular_slab import make_rectangular_slab_from_base_foundation


class ExplodeFoundation():
    """Gui command for the Explode Foundation to rectangular slab objects."""


    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_explode_foundation",
            "Explode Foundation")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_explode_foundation",
            "Explode Foundation")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "explode_foundation.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}
    
    def Activated(self):
        """
        Execute when the command is called.
        """
        
        # The command to run is built as a series of text strings
        # to be committed through the `draftutils.todo.ToDo` class.
        sel = Gui.Selection.getSelection()
        if not sel:
            show_warning()
            return
        foun = None
        for o in sel:
            if hasattr(o, "IfcType") and o.IfcType == 'Footing':
                foun = o
                break
        if foun is None:
            show_warning()
            return
        try:
            FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Explode Foundation"))
            for bf in foun.base_foundations:
                make_rectangular_slab_from_base_foundation(bf)
            remove_obj(foun.Name)
            FreeCAD.ActiveDocument.commitTransaction()
        except Exception:
            _err("Draft: error delaying commit")

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

def remove_obj(name: str) -> None:
    o = FreeCAD.ActiveDocument.getObject(name)
    if hasattr(o, "Base") and o.Base:
        remove_obj(o.Base.Name)
    FreeCAD.ActiveDocument.removeObject(name)

def show_warning():
    QMessageBox.warning(None, 'Selection', 'Please select the foundation!')

Gui.addCommand('osafe_explode_foundation', ExplodeFoundation())

## @}
