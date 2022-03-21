# ***************************************************************************
# *   (c) 2009 Yorik van Havre <yorik@uncreated.net>                        *
# *   (c) 2010 Ken Cline <cline@frii.com>                                   *
# *   (c) 2020 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>           *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Provides GUI tools to create BSpline objects.

See https://en.wikipedia.org/wiki/B-spline
"""
## @package gui_splines
# \ingroup draftguitools
# \brief Provides GUI tools to create BSpline objects.

## \addtogroup draftguitools
# @{
from pathlib import Path
import FreeCAD
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCADGui as Gui
import draftutils.utils as utils
import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original
import draftguitools.gui_tool_utils as gui_tool_utils
import draftguitools.gui_lines as gui_lines
import draftguitools.gui_trackers as trackers

from draftutils.messages import _msg, _err
from draftutils.translate import translate


class BSpline(gui_lines.Line):
    """Gui command for the BSpline tool."""

    def __init__(self):
        super(BSpline, self).__init__(wiremode=True)

    def GetResources(self):
        """Set icon, menu and tooltip."""

        return {'Pixmap': 'Draft_BSpline',
                'Accel': "B, S",
                'MenuText': QT_TRANSLATE_NOOP("Draft_BSpline", "B-spline"),
                'ToolTip': QT_TRANSLATE_NOOP("Draft_BSpline", "Creates a multiple-point B-spline. CTRL to snap, SHIFT to constrain.")}

    def Activated(self):
        """Execute when the command is called.

        Activate the specific BSpline tracker.
        """
        super(BSpline, self).Activated(name=translate("draft", "BSpline"))
        # if self.doc:
        #     self.linetrack = trackers.lineTracker()
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        self.bf_width = p.GetFloat("base_foundation_width",1000)
        self.bf_height = p.GetFloat("base_foundation_height",1000)
        self.bf_soil_modulus = p.GetFloat("base_foundation_soil_modulus",2)
        self.base_foundation_ui = self.taskbox()
        self.ui.layout.insertWidget(0, self.base_foundation_ui)

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view
        by the `Activated` method of the parent class.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":  # mouse movement detection
            (self.point,
             ctrlPoint, info) = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()
        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):
            if arg["Position"] == self.pos:
                self.finish(False, cont=True)

            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                (self.point,
                 ctrlPoint, info) = gui_tool_utils.getPoint(self, arg,
                                                            noTracker=True)
            if self.point:
                self.ui.redraw()
                self.pos = arg["Position"]
                self.node.append(self.point)
                self.drawUpdate(self.point)
                if not self.isWire and len(self.node) == 2:
                    self.finish(False, cont=True)
                if len(self.node) > 2:
                    # DNC: allows to close the curve
                    # by placing ends close to each other
                    # with tol = Draft tolerance
                    # old code has been to insensitive
                    if (self.point - self.node[0]).Length < utils.tolerance():
                        self.undolast()
                        self.finish(True, cont=True)
                        _msg(translate("draft",
                                       "Spline has been closed"))

    def undolast(self):
        """Undo last line segment."""
        import Part
        if len(self.node) > 1:
            self.node.pop()
            # self.linetrack.update(self.node)
            spline = Part.BSplineCurve()
            spline.interpolate(self.node, False)
            self.obj.Shape = spline.toShape()
            _msg(translate("draft", "Last point has been removed"))

    def drawUpdate(self, point):
        """Draw and update to the spline."""
        print('draw update')
        import Part
        if self.planetrack and self.node:
            self.planetrack.set(self.node[-1])
        if len(self.node) == 1:
            # self.linetrack.on()
            _msg(translate("draft", "Pick next point"))
        else:
            spline = Part.BSplineCurve()
            spline.interpolate(self.node, False)
            self.obj.Shape = spline.toShape()
            _msg(translate("draft",
                           "Pick next point, "
                           "or finish (A) or close (O)"))

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the spline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """
        # if self.ui:
            # self.linetrack.finalize()
        if not utils.getParam("UiMode", 1):
            Gui.Control.closeDialog()
        if self.obj:
            # Remove temporary object, if any
            old = self.obj.Name
            todo.ToDo.delay(self.doc.removeObject, old)
        if len(self.node) > 1:
            # The command to run is built as a series of text strings
            # to be committed through the `draftutils.todo.ToDo` class.
            try:
                rot, sup, pts, fil = self.getStrings()
                Gui.addModule("Draft")

                _cmd = 'Draft.makeBSpline'
                _cmd += '('
                _cmd += 'points, '
                _cmd += 'closed=' + str(closed) + ', '
                _cmd += 'face=' + fil + ', '
                _cmd += 'support=' + sup
                _cmd += ')'
                _cmd_list = ['points = ' + pts,
                             'spline = ' + _cmd,
                             'Draft.autogroup(spline)',
                             'FreeCAD.ActiveDocument.recompute()']
                self.commit(translate("draft", "Create B-spline"),
                            _cmd_list)
            except Exception:
                _err("Draft: error delaying commit")

        # `Creator` is the grandfather class, the parent of `Line`;
        # we need to call it to perform final cleanup tasks.
        #
        # Calling it directly like this is a bit messy; maybe we need
        # another method that performs cleanup (superfinish)
        # that is not re-implemented by any of the child classes.
        gui_base_original.Creator.finish(self)
        if self.ui and self.ui.continueMode:
            self.Activated()

    def numericInput(self, numx, numy, numz):
        """Validate the entry fields in the user interface.

        This function is called by the toolbar or taskpanel interface
        when valid x, y, and z have been entered in the input fields.
        """
        print(f'numeric ({numx}, {numy}, {numz})')
        self.point = FreeCAD.Vector(numx, numy, numz)
        self.node.append(self.point)
        self.drawUpdate(self.point)
        if not self.isWire and len(self.node) == 2:
            self.finish(False, cont=True)
        self.ui.setNextFocus()

    def taskbox(self):

        "sets up a taskbox widget"
        punch_path = Path(__file__).parent
        w = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'base_foundation.ui'))
    
        self.layer_name_combo = w.strip_layer
        self.width_spin = w.width_spinbox
        self.height_spin = w.height_spinbox
        self.soil_modulus_spin = w.soil_modulus
        # self.layer_name_combo.setValue(self.bx / 10))
        self.width_spin.setValue(int(self.bf_width / 10))
        self.height_spin.setValue(int(self.bf_height / 10))
        self.soil_modulus_spin.setValue(self.bf_soil_modulus)

        # connect slotsx
        # self.width_spin.valueChanged.connect(self.set_width)
        # self.height_spin.valueChanged.connect(self.set_height)
        # self.soil_modulus_spin.valueChanged.connect(self.set_soil_modulus)
        return w


Gui.addCommand('OSAFE_BSpline', BSpline())

## @}
