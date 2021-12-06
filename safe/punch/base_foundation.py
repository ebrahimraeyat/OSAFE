from pathlib import Path
from typing import Union
from PySide2 import QtCore
import FreeCAD
from safe.punch import punch_funcs


def make_base_foundation(
        beams : list,
        layer : str,
        design_type : str,
        width : float = 1000,
        height : float = 1000,
        # soil_modulus : float =2,
        left_width : Union[float, bool] = None,
        right_width : Union[float, bool] = None,
        ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "BaseFoundation")
    BaseFoundation(obj)
    obj.beams = beams
    obj.layer = layer
    obj.design_type = design_type
    obj.width = width
    if left_width:
        obj.left_width = left_width
        obj.right_width = width - left_width
    elif right_width:
        obj.right_width = right_width
        obj.left_width = width - right_width
    else:
        obj.left_width = obj.right_width = obj.width / 2
    obj.height = height
    # obj.soil_modulus = soil_modulus
    if FreeCAD.GuiUp:
        ViewProviderBaseFoundation(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class BaseFoundation:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "BaseFoundation"
        self.set_properties(obj)

    def set_properties(self, obj):
        if not hasattr(obj, "points"):
            obj.addProperty(
                "App::PropertyVectorList",
                "points",
                "Geometry",
                )
        if not hasattr(obj, "beams"):
            obj.addProperty(
                "App::PropertyLinkList",
                "beams",
                "base_foundation",
                )
        if not hasattr(obj, "layer"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "layer",
                "strip",
                ).layer = ['A', 'B', 'other']
        if not hasattr(obj, "design_type"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "design_type",
                "strip",
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
        if not hasattr(obj, "height"):
            obj.addProperty(
                "App::PropertyLength",
                "height",
                "Geometry",
                ).height = '1 m'
        if not hasattr(obj, "fix_width_from"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "fix_width_from",
                "Geometry",
                ).fix_width_from = ['center', 'Left', 'Right']
        if not hasattr(obj, "main_wire"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "main_wire",
                "Geometry",
                )
        if not hasattr(obj, "extended_shape"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_shape",
                "Geometry",
                )
        if not hasattr(obj, "extended_first_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_first_edge",
                "Geometry",
                )
        if not hasattr(obj, "extended_last_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_last_edge",
                "Geometry",
                )
        if not hasattr(obj, "first_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "first_edge",
                "Geometry",
                )
        if not hasattr(obj, "last_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "last_edge",
                "Geometry",
                )
        if not hasattr(obj, "main_wire_first_point"):
            obj.addProperty(
                "App::PropertyVector",
                "main_wire_first_point",
                "Geometry",
                )
        if not hasattr(obj, "main_wire_last_point"):
            obj.addProperty(
                "App::PropertyVector",
                "main_wire_last_point",
                "Geometry",
                )
        if not hasattr(obj, "final_wire_first_point"):
            obj.addProperty(
                "App::PropertyVector",
                "final_wire_first_point",
                "Geometry",
                )
        if not hasattr(obj, "final_wire_last_point"):
            obj.addProperty(
                "App::PropertyVector",
                "final_wire_last_point",
                "Geometry",
                )
        obj.setEditorMode('points', 2)
        obj.setEditorMode('main_wire_first_point', 2)
        obj.setEditorMode('main_wire_last_point', 2)
        obj.setEditorMode('final_wire_first_point', 2)
        obj.setEditorMode('final_wire_last_point', 2)

    def execute(self, obj):
        if obj.width.Value == 0:
            return
        if obj.layer == 'A':
            obj.ViewObject.ShapeColor = (1.00,0.00,0.20)
        elif obj.layer == 'B':
            obj.ViewObject.ShapeColor = (0.20,0.00,1.00)
        elif obj.layer == 'other':
            obj.ViewObject.ShapeColor = (0.20,1.00,0.00)
        if obj.fix_width_from == 'Left':
            sl = obj.left_width.Value
            sr = obj.width.Value - sl
        elif obj.fix_width_from == 'Right':
            sr = obj.right_width.Value
            sl = obj.width.Value - sr
        elif obj.fix_width_from == 'center':
            sr = sl = obj.width.Value / 2
        shape, main_wire, _, _ = punch_funcs.make_base_foundation_shape_from_beams(obj.beams, sl, sr)
        extended_main_wire, e1, e2, p1, p2 = punch_funcs.get_extended_wire(main_wire)
        obj.extended_first_edge = e1
        obj.extended_last_edge = e2
        obj.main_wire_first_point = p1
        obj.main_wire_last_point = p2
        obj.extended_shape, *_ = punch_funcs.get_left_right_offset_wire_and_shape(extended_main_wire, sl, sr)
        obj.main_wire = main_wire
        obj.Shape = shape


class ViewProviderBaseFoundation:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.Transparency = 80
        vobj.DisplayMode = "Shaded"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = [FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.beams]
        return children

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "base_foundation.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def onDelete(self, vobj, subelements):
        for o in FreeCAD.ActiveDocument.Objects:
            if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'Foundation':
                base_names = [b.Name for b in o.base_foundations]
                if self.Object.Name in base_names:
                    base_names.remove(self.Object.Name)
                    base_foundations = [FreeCAD.ActiveDocument.getObject(name) for name in base_names]
                    o.base_foundations = base_foundations
        return True
        

if __name__ == "__main__":
    from safe.punch.rectangle_slab import make_beam
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1000, 0, 0)
    p3 = FreeCAD.Vector(3000, 2000, 0)
    b1 = make_beam(p1, p2)
    b2 = make_beam(p2, p3)
    make_base_foundation(
            beams=[b1, b2],
            layer='other',
            design_type='column',
            )
