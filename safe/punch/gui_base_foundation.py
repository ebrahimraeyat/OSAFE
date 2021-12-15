
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui
import Draft
import DraftVecUtils

from draftutils.translate import translate
from draftguitools.gui_lines import Line


class BaseFoundation(Line):
    """Gui command for the Beam tool."""

    def __init__(self, wiremode=True):
        super().__init__()
        self.isWire = wiremode

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_base_foundation",
            "Create base_foundation")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_base_foundation",
            "Create base_foundation")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "base_foundation.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the polyline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """
        self.removeTemporaryObject()
        if self.oldWP:
            FreeCAD.DraftWorkingPlane = self.oldWP
            if hasattr(Gui, "Snapper"):
                Gui.Snapper.setGrid()
                Gui.Snapper.restack()
        self.oldWP = None

        if len(self.node) > 1:
            points_string = [DraftVecUtils.toString(p) for p in self.node]
            if closed == True:
                points_string.append(DraftVecUtils.toString(self.node[0]))
            cmd_list = [
                    'from safe.punch.beam import make_beam',
                    'from safe.punch.base_foundation import make_base_foundation',
                    'beams = []',
                    ]
            for p1, p2 in zip(points_string[:-1], points_string[1:]):
                cmd_list.append(f'beam = make_beam({p1}, {p2})')
                cmd_list.append(f'beams.append(beam)')
            cmd_list.append(f'make_base_foundation(beams)')
            self.commit(translate("civil", "Create Base Foundation"),
                        cmd_list)
        super(Line, self).finish()
        
        if self.ui and self.ui.continueMode:
            self.Activated()