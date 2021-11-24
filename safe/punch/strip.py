from pathlib import Path
from typing import Union
from PySide2 import QtCore
import Part
import FreeCAD
from safe.punch import punch_funcs


def make_strip_segment(start_point, end_point, swl, swr, ewl, ewr):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Segment")
    StripSegment(obj)
    obj.start_point = start_point
    obj.end_point = end_point
    obj.start_width_left = swl
    obj.start_width_right = swr
    obj.end_width_left = ewl
    obj.end_width_right = ewr
    if FreeCAD.GuiUp:
        ViewProviderStripSegment(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj

def make_strip(
        points,
        layer,
        design_type,
        segments : Union[list, bool] = None,
        ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Strip")
    Strip(obj)
    obj.points = points
    obj.layer = layer
    obj.design_type = design_type
    if segments is not None:
        obj.segments = segments
    if FreeCAD.GuiUp:
        ViewProviderStrip(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class StripSegment:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        if not hasattr(obj, "start_width_left"):
            obj.addProperty(
                "App::PropertyLength",
                "start_width_left",
                "Segment",
                )
        if not hasattr(obj, "start_width_right"):
            obj.addProperty(
                "App::PropertyLength",
                "start_width_right",
                "Segment",
                )
        if not hasattr(obj, "end_width_left"):
            obj.addProperty(
                "App::PropertyLength",
                "end_width_left",
                "Segment",
                )
        if not hasattr(obj, "end_width_right"):
            obj.addProperty(
                "App::PropertyLength",
                "end_width_right",
                "Segment",
                )
        if not hasattr(obj, "start_point"):
            obj.addProperty(
                "App::PropertyVector",
                "start_point",
                "Segment",
                )
        if not hasattr(obj, "end_point"):
            obj.addProperty(
                "App::PropertyVector",
                "end_point",
                "Segment",
                )
        if not hasattr(obj, "height"):
            obj.addProperty(
                "App::PropertyLength",
                "height",
                "Segment",
                )
        obj.setEditorMode("start_point", 2)
        obj.setEditorMode("end_point", 2)
        obj.setEditorMode("end_width_left", 2)
        obj.setEditorMode("end_width_right", 2)
        obj.setEditorMode("height", 2)


    def execute(self, obj):
        p1 = obj.start_point
        p2 = obj.end_point
        obj.Shape = Part.makeLine(p1, p2)


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
        if not hasattr(obj, "segments"):
            obj.addProperty(
                "App::PropertyLinkList",
                "segments",
                "Strip",
                )
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
        
    # def onChanged(self, obj, prop):
    #     if prop != 'points':
    #         obj.redraw = False

    def execute(self, obj):
        # if obj.redraw:
        #     obj.redraw = False
        #     return
        self._execute()
        # QtCore.QTimer().singleShot(50, self._execute)

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
        if obj.width.Value > 0:
            if obj.fix_width_from == 'Left':
                sl = obj.left_width.Value
                sr = obj.width.Value - sl
            elif obj.fix_width_from == 'Right':
                sr = obj.right_width.Value
                sl = obj.width.Value - sr
            elif obj.fix_width_from == 'center':
                sr = sl = obj.width.Value / 2
        shapes = []
        segments = obj.segments
        for i, p in enumerate(obj.points[:-1]):
            p1 = p
            p2 = obj.points[i + 1]
            if obj.width.Value == 0:
                if len(segments) <= i:
                    sl = obj.left_width.Value
                    sr = obj.right_width.Value
                    segment = make_strip_segment(p1, p2, sl, sr, sl, sr)
                    segments.append(segment)
                else:
                    segment = segments[i]
                sl = segment.start_width_left.Value
                sr = segment.start_width_right.Value
            offset = (sl - sr) / 2
            width = (sl + sr) / 2 # width is half of slab width
            p1, p2 = punch_funcs.get_offset_points(p1, p2, offset)
            points = punch_funcs.get_width_points(p1, p2, width)
            points.append(points[0])
            shapes.append(Part.Face(Part.makePolygon(points)))
        obj.segments = segments
        comm = punch_funcs.get_common_part_of_strips(obj.points, offset, width)
        if len(shapes) > 1:
            fusion = shapes[0].fuse(shapes[1:] + comm)
            faces = fusion.Faces
            fusion = faces[0].fuse(faces[1:])
            obj.Shape = fusion.removeSplitter()
        else:
            obj.Shape = shapes[0]
        # FreeCAD.ActiveDocument.recompute()


class ViewProviderStripSegment:
    def __init__(self, vobj):
        vobj.Proxy = self        

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    # def getIcon(self):
    #     return str(Path(__file__).parent / "Resources" / "icons" / "strip.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None



class ViewProviderStrip:
    def __init__(self, vobj):
        vobj.Proxy = self        

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = [FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.segments]
        return children

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "strip.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def onDelete(self, vobj, subelements):
        for name in [o.Name for o in self.Object.segments]:
            FreeCAD.ActiveDocument.removeObject(name)
        return True
        

if __name__ == "__main__":
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(5000, 0, 0)
    p3 = FreeCAD.Vector(8000, 2000, 0)
    p4 = FreeCAD.Vector(12000, 3000, 0)
    points=[p1, p2, p3, p4]
    sl = 300
    sr = 700
    make_strip(
            points=[p1, p2],
            layer='B',
            design_type='column',
            )
    make_strip(
            points=[p1, p2, p3],
            layer='B',
            design_type='column',
            )
    make_strip(
            points=[p1, p2, p3, p4],
            layer='other',
            design_type='column',
            )
