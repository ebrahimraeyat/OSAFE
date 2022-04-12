from pathlib import Path
from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD

import FreeCADGui as Gui

from draftutils.messages import _msg, _err
from draftutils.translate import translate

from safe.punch.rectangular_slab import make_rectangular_slab


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
            return
        foun = None
        for o in sel:
            if hasattr(o, "IfcType") and o.IfcType == 'Footing':
                foun = o
                break
        if foun is None:
            return
        try:
            # rot, sup, pts, fil = self.getStrings()
            hide_beams = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetBool("base_foundation_hide_beams", True)
            FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Explode Foundation"))
            for bf in foun.base_foundations:
                make_rectangular_slab(bf.beams, bf.layer, bf.width, bf.height, bf.ks, bf.align, bf.left_width, bf.right_width, hide_beams)
            
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

Gui.addCommand('osafe_explode_foundation', ExplodeFoundation())

## @}
