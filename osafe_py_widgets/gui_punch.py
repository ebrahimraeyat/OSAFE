
from pathlib import Path

from PySide import QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui
import Draft
from draftutils.translate import translate

from osafe_objects.punch import make_punch


class Punch:
    """Gui command for the Punch."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_punch",
            "Create punch")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "civil_punch",
            "Create punch")
        path = str(
                   Path(__file__).parent.parent / "osafe_images" / "punch.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        def is_foundation_type(obj):
            if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, 'Type') and obj.Proxy.Type == 'Foundation':
                return True
            return False

        doc = FreeCAD.ActiveDocument
        sel = Gui.Selection.getSelection()
        foun = None
        if sel and is_foundation_type(sel[0]):
                foun = sel[0]
        if foun is None:
            for o in doc.Objects:
                if is_foundation_type(o):
                    foun = o
                    break
        if foun is None:
            return
        FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Create Punches"))
        if hasattr(doc, 'Punches'):
            punches = doc.Punches
            columns = [punch.column.Name for punch in punches.Group]
        else:
            punches = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Punches")
            columns = []
        for o in doc.Objects:
            if hasattr(o, 'IfcType') and \
                o.IfcType == 'Column' and \
                    hasattr(o, 'combos_load') and \
                        hasattr(o, 'Base'):
                if o.Name in columns:
                    continue
                punch = make_punch(
                    foun,
                    o,
                    )
                l = punch.Location
                pl = FreeCAD.Vector(0, 0, o.Shape.BoundBox.ZMax)
                t = '0.0'
                text = Draft.make_text([t, l], placement=pl)
                punch.Ratio = t
                if FreeCAD.GuiUp:
                    text.ViewObject.FontSize = 200
                punch.text = text
                punch.id = o.Label
                punches.addObject(punch)
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.ActiveDocument.commitTransaction()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None