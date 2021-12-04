from pathlib import Path
from typing import Union
from PySide2 import QtCore
import Part
import FreeCAD
from safe.punch import punch_funcs


def make_base_foundation(
        beams : list,
        layer : str,
        design_type : str,
        width : float = 1000,
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
    if FreeCAD.GuiUp:
        ViewProviderBaseFoundation(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class BaseFoundation:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "BaseFoundation"
        self.set_properties(obj)
        self.obj_name = obj.Name

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
        if not hasattr(obj, "redraw"):
            obj.addProperty(
                "App::PropertyBool",
                "redraw",
                "base_foundation",
                ).redraw = False
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
        if not hasattr(obj, "fix_width_from"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "fix_width_from",
                "Geometry",
                ).fix_width_from = ['center', 'Left', 'Right']
        if not hasattr(obj, "left_wire"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "left_wire",
                "Geometry",
                )
        if not hasattr(obj, "right_wire"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "right_wire",
                "Geometry",
                )
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
        if not hasattr(obj, "cut_shapes"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "cut_shapes",
                "Geometry",
                )
        if not hasattr(obj, "first_common_shape"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "first_common_shape",
                "Geometry",
                )
        if not hasattr(obj, "last_common_shape"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "last_common_shape",
                "Geometry",
                )
        if not hasattr(obj, "base_shape"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "base_shape",
                "Geometry",
                "the shape that created from beams",
                )
            
        obj.setEditorMode('points', 2)
        obj.setEditorMode('main_wire_first_point', 2)
        obj.setEditorMode('main_wire_last_point', 2)
        obj.setEditorMode('final_wire_first_point', 2)
        obj.setEditorMode('final_wire_last_point', 2)

    def onChanged(self, obj, prop):
        print(f'onChanged {obj.Name}, {prop}')
    
    def execute(self, obj):
        print(f'Executed {obj.Name}')
        if obj.width.Value == 0:
            return
    #     if obj.redraw:
    #         obj.redraw = False
    #         return
    #     QtCore.QTimer().singleShot(50, self._execute)

    # def _execute(self):
    #     obj = FreeCAD.ActiveDocument.getObject(self.obj_name)
    #     if not obj:
    #         FreeCAD.ActiveDocument.recompute()
    #         return
    #     obj.redraw = True
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
        shape, main_wire, left_wire, right_wire = punch_funcs.make_base_foundation_shape_from_beams(obj.beams, sl, sr)
        extended_main_wire, e1, e2, p1, p2 = punch_funcs.get_extended_wire(main_wire)
        obj.base_shape = shape
        obj.extended_first_edge = e1
        obj.extended_last_edge = e2
        obj.main_wire_first_point = p1
        obj.main_wire_last_point = p2
        obj.extended_shape, *_ = punch_funcs.get_left_right_offset_wire_and_shape(extended_main_wire, sl, sr)
        obj.left_wire = left_wire
        obj.right_wire = right_wire
        obj.main_wire = main_wire
        shape = [shape]
        if not obj.first_common_shape.isNull():
            shape.append(obj.first_common_shape)
        if not obj.last_common_shape.isNull():
            shape.append(obj.last_common_shape)
        # if not obj.first_edge.isNull():
        #     shape.append(obj.first_edge)
        # if not obj.last_edge.isNull():
        #     shape.append(obj.last_edge)
        # shape.append(obj.main_wire)
        if len(shape) > 1:
            shape = shape[0].fuse(shape[1:])
            shape = shape.removeSplitter()
        else:
            shape = shape[0]
        if not obj.cut_shapes.isNull():
            shape = shape.cut(obj.cut_shapes)
        obj.Shape = shape
        # FreeCAD.ActiveDocument.recompute()


class ViewProviderBaseFoundation:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.Transparency = 80
        vobj.DisplayMode = "Flat Lines"

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

    # def onDelete(self, vobj, subelements):
    #     for name in [o.Name for o in self.Object.segments]:
    #         FreeCAD.ActiveDocument.removeObject(name)
    #     return True
        

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
