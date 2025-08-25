
from pathlib import Path

from PySide import QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP
from PySide.QtGui import QMessageBox

import FreeCAD
import FreeCADGui as Gui
import Draft
from draftutils.translate import translate

from find_etabs import find_etabs


class UpdateReactionForces:
    """Gui command for Update Reaction Forces."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "osafe_update_reaction_forces",
            "Update Reaction Forces")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "osafe_update_reaction_forces",
            "Update Reaction Forces Frome ETABS to OSAFE")
        path = str(
                   Path(__file__).parent.parent.parent / "osafe_images" / "update_reaction_forces.png"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(
            run=True,
            )
        if (
            etabs is None or
            filename is None
            ):
            return
        doc = FreeCAD.ActiveDocument
        if doc is None:
            QMessageBox.warning(None, 'OSAFE File', 'Please Open OSAFE File and try again.')
            return
        if hasattr(doc, 'Safe') and hasattr(doc.Safe, 'input'):
            filename = doc.Safe.input
        else:
            filename = None
        if not filename:
            QMessageBox.warning(None, 'Input F2k File', 'There is no input F2k file in file, Please select input F2k file.')
            return

        if filename and not Path(filename).exists():
            QMessageBox.warning(None, 'Wrong File', f'Safe F2K file {filename} does not exist.')
            return
        from osafe_py_widgets.modify_f2k import update_point_reactions
        f = update_point_reactions.Form(etabs, filename)
        f.update_point_loads()

        # for o in doc.Objects:
        #     if hasattr(o, 'IfcType') and \
        #         o.IfcType == 'Column' and \
        #             hasattr(o, 'combos_load') and \
        #                 hasattr(o, 'Base'):
        #         if o.Name in columns:
        #             continue
        #         punch = make_punch(
        #             foun,
        #             o,
        #             )
        #         l = punch.Location
        #         pl = FreeCAD.Vector(0, 0, o.Shape.BoundBox.ZMax)
        #         t = '0.0'
        #         text = Draft.make_text([t, l], placement=pl)
        #         punch.Ratio = t
        #         if FreeCAD.GuiUp:
        #             text.ViewObject.FontSize = 200
        #         punch.text = text
        #         punch.id = o.Label
        #         punches.addObject(punch)
        # FreeCAD.ActiveDocument.recompute()
        # FreeCAD.ActiveDocument.commitTransaction()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
    
Gui.addCommand('osafe_update_reaction_forces', UpdateReactionForces())