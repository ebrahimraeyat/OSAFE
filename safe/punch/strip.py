from pathlib import Path
from typing import Union
from PySide2 import QtCore
import Part
import FreeCAD
from safe.punch import punch_funcs


def make_strip(
        beams : list,
        layer : str,
        design_type : str,
        width : float = 1000,
        left_width : Union[float, bool] = None,
        right_width : Union[float, bool] = None,
        ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Strip")
    Strip(obj)
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
        ViewProviderStrip(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Strip:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "Strip"
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
        if not hasattr(obj, "redraw"):
            obj.addProperty(
                "App::PropertyBool",
                "redraw",
                "Strip",
                ).redraw = False
        if not hasattr(obj, "left_width"):
            obj.addProperty(
                "App::PropertyLength",
                "left_width",
                "Strip",
                ).left_width = '0.5 m'
        if not hasattr(obj, "right_width"):
            obj.addProperty(
                "App::PropertyLength",
                "right_width",
                "Strip",
                ).right_width = '0.5 m'
        if not hasattr(obj, "width"):
            obj.addProperty(
                "App::PropertyLength",
                "width",
                "Strip",
                ).width = '1 m'
        if not hasattr(obj, "fix_width_from"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "fix_width_from",
                "Strip",
                ).fix_width_from = ['center', 'Left', 'Right']
        obj.setEditorMode('points', 2)

    def execute(self, obj):
        if obj.width.Value == 0:
            return
        if obj.redraw:
            obj.redraw = False
            return
        QtCore.QTimer().singleShot(50, self._execute)

    def _execute(self):
        obj = FreeCAD.ActiveDocument.getObject(self.obj_name)
        if not obj:
            FreeCAD.ActiveDocument.recompute()
            return
        obj.redraw = True
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
        shapes = []
        obj.points = punch_funcs.get_sort_points_from_slabs(obj.beams)
        for i, p in enumerate(obj.points[:-1]):
            p1 = p
            p2 = obj.points[i + 1]
            offset = (sl - sr) / 2
            width = (sl + sr) / 2 # width is half of slab width
            p1, p2 = punch_funcs.get_offset_points(p1, p2, offset)
            points = punch_funcs.get_width_points(p1, p2, width)
            points.append(points[0])
            shapes.append(Part.Face(Part.makePolygon(points)))
        comm = punch_funcs.get_common_part_of_strips(obj.points, offset, width)
        if len(shapes) > 1:
            fusion = shapes[0].fuse(shapes[1:] + comm)
            faces = fusion.Faces
            fusion = faces[0].fuse(faces[1:])
            obj.Shape = fusion.removeSplitter()
        else:
            obj.Shape = shapes[0]
        FreeCAD.ActiveDocument.recompute()


class ViewProviderStripSegment:
    def __init__(self, vobj):
        vobj.Proxy = self      

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "segment.png")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None



class ViewProviderStrip:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.Transparency = 40
        vobj.DisplayMode = "Shaded"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = [FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.beams]
        return children

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "strip.svg")

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
    make_strip(
            beams=[b1, b2],
            layer='other',
            design_type='column',
            )
