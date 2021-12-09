
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui
import Draft
import DraftVecUtils

from draftutils.translate import translate
from draftguitools.gui_lines import Line


class Slab(Line):
    """Gui command for the Slab tool."""

    def __init__(self, wiremode=True):
        super().__init__()
        self.isWire = wiremode

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_slab",
            "Create slab")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_slab",
            "Create slab")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "slab.svg"
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

        if len(self.node) > 2:
            Gui.addModule("Draft")
            # The command to run is built as a series of text strings
            # to be committed through the `draftutils.todo.ToDo` class.
            
            # Insert a Draft wire
            rot, sup, pts, fil = self.getStrings()

            _base = DraftVecUtils.toString(self.node[0])
            _cmd = 'Draft.makeWire'
            _cmd += '('
            _cmd += 'points, '
            _cmd += 'placement=pl, '
            _cmd += 'closed=' + str(closed) + ', '
            _cmd += 'face=' + fil + ', '
            _cmd += 'support=' + sup
            _cmd += ')'
            _cmd_list = [
                        'pl = FreeCAD.Placement()',
                        'pl.Rotation.Q = ' + rot,
                        'pl.Base = ' + _base,
                        'points = ' + pts,
                        'line = ' + _cmd,
                        'Draft.autogroup(line)',
                        'FreeCAD.ActiveDocument.recompute()',
                        'from safe.punch.slab import make_slab',
                        'make_slab(line)',
                        'line.ViewObject.hide()',
                        ]
            self.commit(translate("civil", "Create Slab"),
                        _cmd_list)
        super(Line, self).finish()
        
        if self.ui and self.ui.continueMode:
            self.Activated()

Gui.addCommand('civil_slab', Slab())
