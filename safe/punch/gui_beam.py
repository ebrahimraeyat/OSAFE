
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui
import Draft
import DraftVecUtils

from draftutils.translate import translate
from draftguitools.gui_lines import Line


class Beam(Line):
    """Gui command for the Beam tool."""

    def __init__(self, wiremode=True):
        super().__init__()
        self.isWire = wiremode

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_beam",
            "Create beam")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_beam",
            "Create beam")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "beam.svg"
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
            cmd_list = ['from safe.punch.beam import make_beam']
            for p1, p2 in zip(points_string[:-1], points_string[1:]):
                if DraftVecUtils.equals(p1, p2):
                    continue
                cmd_list.append(f'make_beam({p1}, {p2})')
            self.commit(translate("civil", "Create beam"),
                        cmd_list)
        super(Line, self).finish()
        Gui.Selection.clearSelection()
        if self.ui and self.ui.continueMode:
            self.Activated()