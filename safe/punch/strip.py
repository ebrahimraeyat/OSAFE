from pathlib import Path
from typing import Union
from PySide2 import QtCore
import FreeCAD
import Part
from safe.punch import punch_funcs


def make_strip(
        points : list,
        layer : str = 'A',
        design_type : str = 'column',
        width : float = 1000,
        left_width : float = 0,
        right_width : float = 0,
        align : str = 'Center',
        ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Strip")
    Strip(obj)
    obj.points = points
    obj.layer = layer
    obj.design_type = design_type
    obj.width = width
    obj.left_width = left_width
    obj.right_width = right_width
    obj.align = align
    if FreeCAD.GuiUp:
        ViewProviderStrip(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Strip:
    def __init__(self, obj):
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.Proxy = self
        self.Type = "Strip"
        if not hasattr(obj, "points"):
            obj.addProperty(
                "App::PropertyVectorList",
                "points",
                "Strip",
                )
        if not hasattr(obj, "layer"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "layer",
                "Strip",
                ).layer = ['A', 'B', 'other']
        if not hasattr(obj, "design_type"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "design_type",
                "Strip",
                ).design_type = ['column']
        if not hasattr(obj, "left_width"):
            obj.addProperty(
                "App::PropertyLength",
                "left_width",
                "Geometry",
                ).left_width = '0.5 m'
        if not hasattr(obj, "right_width"):
            obj.addProperty(
                "App::PropertyLength",
                "right_width",
                "Geometry",
                ).right_width = '0.5 m'
        if not hasattr(obj, "width"):
            obj.addProperty(
                "App::PropertyLength",
                "width",
                "Geometry",
                ).width = '1 m'
        if not hasattr(obj, "align"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "align",
                "Geometry",
                ).align = ['Center', 'Left', 'Right']
        if not hasattr(obj, "plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan",
                "Geometry",
                )
        if not hasattr(obj, 'show_width'):
            obj.addProperty(
                "App::PropertyBool",
                'show_width',
                'Strip',
            ).show_width = True

    def execute(self, obj):
        if obj.width.Value == 0:
            return
        if obj.layer == 'A':
            obj.ViewObject.ShapeColor = obj.ViewObject.LineColor = (1.00,0.00,0.20)
        elif obj.layer == 'B':
            obj.ViewObject.ShapeColor = obj.ViewObject.LineColor = (0.20,0.00,1.00)
        elif obj.layer == 'other':
            obj.ViewObject.ShapeColor = obj.ViewObject.LineColor = (0.20,1.00,0.00)
        if obj.align == 'Left':
            sl = obj.left_width.Value
            sr = obj.width.Value - sl
            obj.right_width.Value = sr
        elif obj.align == 'Right':
            sr = obj.right_width.Value
            sl = obj.width.Value - sr
            obj.left_width.Value = sl
        elif obj.align == 'Center':
            sr = sl = obj.width.Value / 2
            obj.left_width.Value = sl
            obj.right_width.Value = sr
        wire = Part.makePolygon(obj.points)
        if obj.show_width:
            shape, left_wire, right_wire = punch_funcs.get_left_right_offset_wire_and_shape(wire, sl, sr)
            obj.Shape = Part.makeCompound([shape, wire])
        else:
            obj.Shape = wire

    def onDocumentRestored(self, obj):
        # super().onDocumentRestored(obj)
        self.set_properties(obj)



class ViewProviderStrip:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.Transparency = 80
        vobj.DisplayMode = "Flat Lines"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "strip.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    # def onDelete(self, vobj, subelements):
    #     for o in FreeCAD.ActiveDocument.Objects:
    #         if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'Foundation':
    #             base_names = [b.Name for b in o.base_foundations]
    #             if self.Object.Name in base_names:
    #                 base_names.remove(self.Object.Name)
    #                 base_foundations = [FreeCAD.ActiveDocument.getObject(name) for name in base_names]
    #                 o.base_foundations = base_foundations
    #     return True
        

if __name__ == "__main__":
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1000, 0, 0)
    p3 = FreeCAD.Vector(3000, 2000, 0)
    # b1 = make_beam(p1, p2)
    # b2 = make_beam(p2, p3)
    make_strip(
            points=[p1, p2, p3],
            layer='other',
            design_type='column',
            )
