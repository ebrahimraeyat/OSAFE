
from pathlib import Path
from PySide2 import QtCore

import FreeCAD
if FreeCAD.GuiUp:
    import FreeCADGui as Gui
    from DraftTools import translate
    import DraftTools
    from draftutils.messages import _msg, _err
    from PySide2.QtCore import QT_TRANSLATE_NOOP
    # import draftguitools.gui_trackers as DraftTrackers
    import draftguitools.gui_base_original as gui_base_original
    import draftguitools.gui_tool_utils as gui_tool_utils
    import draftutils.gui_utils as gui_utils
    import draftutils.utils as utils
    import draftutils.todo as todo
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
import DraftVecUtils

# from draftguitools.gui_lines import Line


class BaseFoundation:
    """Gui command for the Beam tool."""

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

    def Activated(self):
        BaseFoundationClass()


class BaseFoundationClass(DraftTools.Line):
    """Gui command for the Beam tool."""

    def __init__(self, wiremode=True):
        DraftTools.Line.__init__(self,wiremode)
        self.Activated()
        # dialog_path = str(
        #            Path(__file__).parent.absolute() / "Resources" / "ui" / "base_foundation.ui"
        #            )
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE")
        self.bf_width = p.GetFloat("base_foundation_width",1000)
        self.bf_height = p.GetFloat("base_foundation_height",1000)
        self.bf_soil_modulus = p.GetFloat("base_foundation_soil_modulus",2)
        self.base_foundation_ui = self.taskbox()
        self.ui.layout.addWidget(self.base_foundation_ui)
        self.nodes=list()

    # def GetResources(self):
    #     menu_text = QtCore.QT_TRANSLATE_NOOP(
    #         "civil_base_foundation",
    #         "Create base_foundation")
    #     tool_tip = QtCore.QT_TRANSLATE_NOOP(
    #         "civil_base_foundation",
    #         "Create base_foundation")
    #     path = str(
    #                Path(__file__).parent.absolute() / "Resources" / "icons" / "base_foundation.svg"
    #                )
    #     return {'Pixmap': path,
    #             'MenuText': menu_text,
    #             'ToolTip': tool_tip}

    # def Activated(self, name=translate("OSAFE", "base_foundation")):
    #     """Execute when the command is called."""
    #     self.isWire = True
    #     super(BaseFoundation, self).Activated(name)

        # if not self.doc:
        #     return
        # self.obj = None  # stores the temp shape
        # self.oldWP = None  # stores the WP if we modify it
        # if self.isWire:
        #     self.ui.wireUi(name)
        # else:
        #     self.ui.lineUi(name)
        # self.ui.setTitle(name)
        # self.obj = self.doc.addObject("Part::Feature", self.featureName)
        # gui_utils.format_object(self.obj)

        # self.call = self.view.addEventCallback("SoEvent", self.action)
        # _msg(translate("OSAFE", "Pick first point"))

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            print('ESCAPE')
            self.removeTemporaryObject()
            if self.oldWP:
                FreeCAD.DraftWorkingPlane = self.oldWP
                if hasattr(Gui, "Snapper"):
                    Gui.Snapper.setGrid()
                    Gui.Snapper.restack()
            self.oldWP = None
            self.commitList = []
            super().finish()
            return
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "PAD_ENTER":
            print("ENTER")
            self.finish()
        elif arg["Type"] == "SoLocation2Event":
            # print("SoLocation2Event")
            self.point, ctrlPoint, info = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()
        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):
            print('SoMouseButtonEvent')
            if arg["Position"] == self.pos:
                return self.finish(False, cont=True)
            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                (self.point,
                 ctrlPoint, info) = gui_tool_utils.getPoint(self, arg)
            if self.point:
                self.ui.redraw()
                self.pos = arg["Position"]
                self.node.append(self.point)
                self.drawSegment(self.point)
                if not self.isWire and len(self.node) == 2:
                    self.finish(False, cont=True)
                if len(self.node) > 2 and \
                    (self.point - self.node[0]).Length < utils.tolerance():  # The wire is closed
                        self.undolast()
                        if len(self.node) > 2:
                            self.finish(True, cont=True)
                        else:
                            self.finish(False, cont=True)

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
            layer = self.base_foundation_ui.strip_layer.currentText()
            width = self.base_foundation_ui.width_spinbox.value() * 10
            height = self.base_foundation_ui.height_spinbox.value() * 10
            ks = self.base_foundation_ui.soil_modulus.value()
            
            for p1, p2 in zip(points_string[:-1], points_string[1:]):
                cmd_list.append(f'beam = make_beam({p1}, {p2})')
                cmd_list.append(f'beams.append(beam)')
            cmd_list.append(f'make_base_foundation(beams, "{layer}", width={width}, height={height}, soil_modulus={ks})')
            self.commit(translate("civil", "Create Base Foundation"),
                        cmd_list)
        self.cmd_list = []
        super().finish()
        # if self.ui and self.ui.continueMode:
        # if n > 1:
        #     self.Activated()

    # def removeTemporaryObject(self):
    #     """Remove temporary object created."""
    #     if self.obj:
    #         try:
    #             old = self.obj.Name
    #         except ReferenceError:
    #             # object already deleted, for some reason
    #             pass
    #         else:
    #             todo.ToDo.delay(self.doc.removeObject, old)
    #     self.obj = None

    # def undolast(self):
    #     """Undoes last line segment."""
    #     import Part
    #     if len(self.node) > 1:
    #         self.node.pop()
    #         # last = self.node[-1]
    #         if self.obj.Shape.Edges:
    #             edges = self.obj.Shape.Edges
    #             if len(edges) > 1:
    #                 newshape = Part.makePolygon(self.node)
    #                 self.obj.Shape = newshape
    #             else:
    #                 self.obj.ViewObject.hide()
    #             # DNC: report on removal
    #             # _msg(translate("draft", "Removing last point"))
    #             _msg(translate("draft", "Pick next point"))

    # def drawSegment(self, point):
    #     """Draws new line segment."""
    #     import Part
    #     if self.planetrack and self.node:
    #         self.planetrack.set(self.node[-1])
    #     if len(self.node) == 1:
    #         _msg(translate("draft", "Pick next point"))
    #     elif len(self.node) == 2:
    #         last = self.node[len(self.node) - 2]
    #         newseg = Part.LineSegment(last, point).toShape()
    #         self.obj.Shape = newseg
    #         self.obj.ViewObject.Visibility = True
    #         if self.isWire:
    #             _msg(translate("draft", "Pick next point"))
    #     else:
    #         currentshape = self.obj.Shape.copy()
    #         last = self.node[len(self.node) - 2]
    #         if not DraftVecUtils.equals(last, point):
    #             newseg = Part.LineSegment(last, point).toShape()
    #             newshape = currentshape.fuse(newseg)
    #             self.obj.Shape = newshape
    #         _msg(translate("draft", "Pick next point"))

    # def wipe(self):
    #     """Remove all previous segments and starts from last point."""
    #     if len(self.node) > 1:
    #         # self.obj.Shape.nullify()  # For some reason this fails
    #         self.obj.ViewObject.Visibility = False
    #         self.node = [self.node[-1]]
    #         if self.planetrack:
    #             self.planetrack.set(self.node[0])
    #         _msg(translate("draft", "Pick next point"))

    # def orientWP(self):
    #     """Orient the working plane."""
    #     import DraftGeomUtils
    #     if hasattr(FreeCAD, "DraftWorkingPlane"):
    #         if len(self.node) > 1 and self.obj:
    #             n = DraftGeomUtils.getNormal(self.obj.Shape)
    #             if not n:
    #                 n = FreeCAD.DraftWorkingPlane.axis
    #             p = self.node[-1]
    #             v = self.node[-2].sub(self.node[-1])
    #             v = v.negative()
    #             if not self.oldWP:
    #                 self.oldWP = FreeCAD.DraftWorkingPlane.copy()
    #             FreeCAD.DraftWorkingPlane.alignToPointAndAxis(p, n, upvec=v)
    #             if hasattr(Gui, "Snapper"):
    #                 Gui.Snapper.setGrid()
    #                 Gui.Snapper.restack()
    #             if self.planetrack:
    #                 self.planetrack.set(self.node[-1])

    # def numericInput(self, numx, numy, numz):
    #     """Validate the entry fields in the user interface.

    #     This function is called by the toolbar or taskpanel interface
    #     when valid x, y, and z have been entered in the input fields.
    #     """
    #     self.point = FreeCAD.Vector(numx, numy, numz)
    #     self.node.append(self.point)
    #     self.drawSegment(self.point)
    #     if not self.isWire and len(self.node) == 2:
    #         self.finish(False, cont=True)
    #     self.ui.setNextFocus()

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
