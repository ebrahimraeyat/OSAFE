from pathlib import Path
from typing import Union
# from PySide2 import QtCore
import FreeCAD, Draft
import ArchComponent

try:
    from safe.punch import punch_funcs
except:
    import punch_funcs


def make_rectangular_slab(
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
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "RectangularSlab")
    RectangularSlab(obj)
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
    plan, _, _ = punch_funcs.get_left_right_offset_wire_and_shape(obj.Base.Shape, obj.left_width, obj.right_width)
    points = punch_funcs.get_sort_points(plan.Edges)
    plan = Draft.make_wire(points, closed=True)
    # FreeCAD.ActiveDocument.recompute()
    obj.plan = plan
    obj.align = align
    obj.height = height
    obj.ks = soil_modulus
    obj.fc = fc
    if FreeCAD.GuiUp:
        ViewProviderRectangularSlab(obj.ViewObject)
        if obj.Base:
            obj.Base.ViewObject.LineWidth = 3.00
        if obj.plan:
            obj.plan.ViewObject.LineWidth = 3.00
    FreeCAD.ActiveDocument.recompute()
    return obj

def make_rectangular_slab_from_base_foundation(base_foundation, plan=None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "RectangularSlab")
    RectangularSlab(obj)
    obj.Base = base_foundation.Base
    obj.layer = base_foundation.layer
    obj.design_type = base_foundation.design_type
    obj.width = base_foundation.width
    obj.left_width = base_foundation.left_width
    obj.right_width = base_foundation.right_width
    if plan is None:
        plan, _, _ = punch_funcs.get_left_right_offset_wire_and_shape(obj.Base.Shape, obj.left_width, obj.right_width)
    elif plan == 'Auto':
        plan = base_foundation.extended_plan
    if len(plan.Wires) == 1:
        points = punch_funcs.get_sort_points(plan.Edges)
        plan = Draft.make_wire(points, closed=True)
        # FreeCAD.ActiveDocument.recompute()
    else:
        temp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Base")
        temp.Shape = plan
        plan = temp
        
    obj.plan = plan
    obj.align = base_foundation.align
    obj.height = base_foundation.height
    obj.ks = base_foundation.ks
    obj.fc = base_foundation.fc
    if FreeCAD.GuiUp:
        ViewProviderRectangularSlab(obj.ViewObject)
        if obj.Base:
            obj.Base.ViewObject.LineWidth = 3.00
        if obj.plan:
            obj.plan.ViewObject.LineWidth = 3.00
    FreeCAD.ActiveDocument.recompute()
    return obj


class RectangularSlab(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Footing"
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.Proxy = self
        self.Type = "RectangularSlab"
        if not hasattr(obj, "layer"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "layer",
                "Strip",
                # "",
                # 8,
                ).layer = ['A', 'B', 'other']
        if not hasattr(obj, "design_type"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "design_type",
                "Strip",
                "",
                8,
                ).design_type = ['column']
        if not hasattr(obj, "ks"):
            obj.addProperty(
                "App::PropertyFloat",
                "ks",
                "Soil",
                "",
                8,
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
        if not hasattr(obj, "fem_shape"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "fem_shape",
                "Geometry",
                )
        if not hasattr(obj, "plan"):
            obj.addProperty(
                "App::PropertyLink",
                "plan",
                "Geometry",
                "",
                16,
                )
        if not hasattr(obj, "fc"):
            obj.addProperty(
            "App::PropertyPressure",
            "fc",
            "Concrete",
            "",
            8,
            )
        if not hasattr(obj, "Auto_Plan"):
            obj.addProperty(
            "App::PropertyBool",
            "Auto_Plan",
            "Geometry",
            ).Auto_Plan = False

    def execute(self, obj):
        if obj.width.Value == 0:
            return
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
        if obj.Auto_Plan and obj.Base:
            plan, _, _ = punch_funcs.get_left_right_offset_wire_and_shape(obj.Base.Shape, sl, sr)
            points = punch_funcs.get_sort_points(plan.Edges, get_last=True)
            obj.plan.Points = points
        if obj.plan:
            obj.Shape = obj.plan.Shape.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
        if FreeCAD.GuiUp:
            if obj.layer == 'A':
                punch_funcs.format_view_object(
                obj=obj,
                shape_color_entity="slab_a_shape_color",
                line_width_entity="slab_a_line_width",
                transparency_entity="slab_a_transparency",
                display_mode_entity="slab_a_display_mode",
                line_color_entity="slab_a_line_color",
                )
            elif obj.layer == 'B':
                punch_funcs.format_view_object(
                obj=obj,
                shape_color_entity="slab_b_shape_color",
                line_width_entity="slab_a_line_width",
                transparency_entity="slab_a_transparency",
                display_mode_entity="slab_a_display_mode",
                line_color_entity="slab_b_line_color",
                )
            elif obj.layer == 'other':
                punch_funcs.format_view_object(
                obj=obj,
                shape_color_entity="slab_b_shape_color",
                line_width_entity="slab_a_line_width",
                transparency_entity="slab_a_transparency",
                display_mode_entity="slab_a_display_mode",
                line_color_entity="slab_b_line_color",
                )
                color = (0.00,1.00,0.00)
                obj.ViewObject.ShapeColor = obj.ViewObject.LineColor = color
            if obj.Base:
                obj.Base.ViewObject.LineColor = obj.ViewObject.LineColor
                obj.Base.ViewObject.PointColor = obj.ViewObject.PointColor
            if obj.plan:
                obj.plan.ViewObject.LineColor = obj.ViewObject.LineColor
                obj.plan.ViewObject.PointColor = obj.ViewObject.PointColor

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        self.set_properties(obj)

class ViewProviderRectangularSlab:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = []
        if self.Object.Base:
            children.append(FreeCAD.ActiveDocument.getObject(self.Object.Base.Name))
        if self.Object.plan:
            children.append(FreeCAD.ActiveDocument.getObject(self.Object.plan.Name))
        return children

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "rectangular_slab.svg")

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
    FreeCAD.ActiveDocument.recompute()
    make_rectangular_slab(
            base=wire,
            )

    from safe.punch.base_foundation import make_base_foundation
    bf = make_base_foundation(base=wire)
    make_rectangular_slab_from_base_foundation(bf)