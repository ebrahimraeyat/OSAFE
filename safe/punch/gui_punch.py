
from pathlib import Path
import math

from PySide2 import QtCore
from PySide2.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import FreeCADGui as Gui
import Draft

from safe.punch.punch import make_punch


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
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "punch.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        def is_foundation_type(obj):
            if hasattr(obj, 'Proxy') and \
                hasattr(obj.Proxy, 'Type') and \
                    obj.Proxy.Type == 'Foundation':
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
        punches = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Punches")
        for o in doc.Objects:
            if hasattr(o, 'IfcType') and \
                o.IfcType == 'Column' and \
                    hasattr(o, 'combos_load'):
                
                bx = o.Length.Value
                by = o.Width.Value
                if (not bx > 0) or (not by > 0):
                    continue
                center_of_load = o.Placement.Base
                combos_load = o.combos_load
                angle = math.degrees(o.Placement.Rotation.Angle)
                punch = make_punch(
                    foun,
                    bx,
                    by,
                    center_of_load,
                    combos_load,
                    angle=angle,
                    )
                l = punch.Location
                pl = FreeCAD.Vector(0, 0, center_of_load.z + 4100)
                t = '0.0'
                version = FreeCAD.Version()[1]
                if int(version) < 19:
                    text = Draft.makeText([t, l], point=pl)
                else:
                    text = Draft.make_text([t, l], placement=pl)
                punch.Ratio = t
                if FreeCAD.GuiUp:
                    text.ViewObject.FontSize = 200
                punch.text = text
                punch.id = o.Label
                punches.addObject(punch)
        FreeCAD.ActiveDocument.recompute()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None