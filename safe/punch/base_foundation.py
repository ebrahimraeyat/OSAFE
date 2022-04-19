from pathlib import Path
from typing import Union
from PySide2 import QtCore
import FreeCAD
import ArchComponent

from safe.punch import punch_funcs


def make_base_foundation(
        base,
        layer : str = 'A',
        width : float = 1000,
        height : float = 1000,
        soil_modulus : float =2,
        fc : Union[float, str] = '25 MPa',
        align : str = 'Center',
        left_width : Union[float, bool] = None,
        right_width : Union[float, bool] = None,
        design_type : str = 'column',
        ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "BaseFoundation")
    BaseFoundation(obj)
    obj.Base = base
    obj.layer = layer
    obj.design_type = design_type
    obj.width = width
    if align == 'Left':
        obj.left_width = left_width
        obj.right_width = width - left_width
    elif align == 'Right':
        obj.right_width = right_width
        obj.left_width = width - right_width
    elif align == 'Center':
        obj.left_width = obj.right_width = obj.width / 2
    obj.align = align
    obj.height = height
    obj.ks = soil_modulus
    obj.fc = fc
    if FreeCAD.GuiUp:
        vobj = obj.ViewObject
        ViewProviderBaseFoundation(vobj)
        vobj.Transparency = 80
        vobj.DisplayMode = "Flat Lines"
    FreeCAD.ActiveDocument.recompute()
    return obj


class BaseFoundation(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        self.Type = "BaseFoundation"
        self.set_properties(obj)
        obj.Proxy = self

    def set_properties(self, obj):
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
        if not hasattr(obj, "ks"):
            obj.addProperty(
                "App::PropertyFloat",
                "ks",
                "Soil",
                )
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
                "Slab",
                ).height = '1 m'
        if not hasattr(obj, "align"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "align",
                "Geometry",
                ).align = ['Center', 'Left', 'Right']
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
        if not hasattr(obj, "plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan",
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
        if not hasattr(obj, "fc"):
            obj.addProperty(
            "App::PropertyPressure",
            "fc",
            "Concrete",
            )
        obj.setEditorMode('main_wire_first_point', 2)
        obj.setEditorMode('main_wire_last_point', 2)
        obj.setEditorMode('final_wire_first_point', 2)
        obj.setEditorMode('final_wire_last_point', 2)

    def execute(self, obj):
        if obj.width.Value == 0:
            return
        if obj.layer == 'A':
            color = (1.00,0.00,0.20)
        elif obj.layer == 'B':
            color = (0.20,0.00,1.00)
        elif obj.layer == 'other':
            color = (0.20,1.00,0.00)
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = color
        obj.ViewObject.PointColor = color
        obj.ViewObject.LineWidth = 1.00
        obj.ViewObject.PointSize = 1.00
        obj.Base.ViewObject.LineColor = color
        obj.Base.ViewObject.PointColor = color
        obj.Base.ViewObject.LineWidth = 3.00
        if obj.align == 'Left':
            sl = obj.left_width.Value
            sr = obj.width.Value - sl
            obj.right_width = sr
        elif obj.align == 'Right':
            sr = obj.right_width.Value
            sl = obj.width.Value - sr
            obj.left_width = sl
        elif obj.align == 'Center':
            sr = sl = obj.width.Value / 2
            obj.right_width = sr
            obj.left_width = sl

        obj.plan, _, _ = punch_funcs.get_left_right_offset_wire_and_shape(obj.Base.Shape, sl, sr)
        obj.Shape = obj.plan.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
        extended_main_wire, e1, e2, p1, p2 = punch_funcs.get_extended_wire(obj.Base.Shape.Wires[0])
        obj.extended_first_edge = e1
        obj.extended_last_edge = e2
        obj.main_wire_first_point = p1
        obj.main_wire_last_point = p2
        obj.extended_shape, *_ = punch_funcs.get_left_right_offset_wire_and_shape(extended_main_wire, sl, sr)


class ViewProviderBaseFoundation:
    def __init__(self, vobj):
        vobj.Proxy = self
        

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = [FreeCAD.ActiveDocument.getObject(self.Object.Base.Name)]
        return children

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "base_foundation.svg")

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
    import Draft
    wire = Draft.make_wire([p1, p2, p3])
    make_base_foundation(
            base=wire,
            layer='other',
            design_type='column',
            )
