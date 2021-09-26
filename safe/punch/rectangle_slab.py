import math
from pathlib import Path
import Part
import FreeCAD
from etabs_api.frame_obj import FrameObj

def make_rectangle_slab(p1, p2, width=1, height=1, offset=0):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Slab")
    RectangleSlab(obj)
    obj.start_point = p1
    obj.end_point = p2
    obj.width = width
    obj.height = height
    obj.offset = offset
    if FreeCAD.GuiUp:
        ViewProviderRectangle(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class RectangleSlab:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "tape_slab"
        self.set_properties(obj)

    def set_properties(self, obj):
        if not hasattr(obj, "start_point"):
            obj.addProperty(
            "App::PropertyVector",
            "start_point",
            "slab",
            )
        if not hasattr(obj, "end_point"):
            obj.addProperty(
            "App::PropertyVector",
            "end_point",
            "slab",
            )
        if not hasattr(obj, "width"):
            obj.addProperty(
            "App::PropertyLength",
            "width",
            "slab",
            )
        if not hasattr(obj, "height"):
            obj.addProperty(
            "App::PropertyLength",
            "height",
            "slab",
            )
        if not hasattr(obj, "offset"):
            obj.addProperty(
            "App::PropertyFloat",
            "offset",
            "slab",
            )
        if not hasattr(obj, "angle"):
            obj.addProperty(
            "App::PropertyAngle",
            "angle",
            "slab",
            )
        if not hasattr(obj, "plane"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plane",
                "slab",
                )
        if not hasattr(obj, "solid"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "solid",
                "slab",
                )

    def onChanged(self, obj, prop):
        return

    def execute(self, obj):
        p1 = obj.start_point
        p2 = obj.end_point
        obj.Shape = Part.makeLine(p1, p2)
        v = p2 - p1
        obj.angle = math.atan2(v.y, v.x)
        self.create_width(obj)

    def create_width(self, obj):
        xs, ys, xe, ye = self.get_new_points(obj)
        points = []
        w = obj.width.Value / 2
        teta = obj.angle
        _sin = math.sin(teta)
        _cos = math.cos(teta)
        x = xs - w * _sin
        y = ys + w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xs + w * _sin
        y = ys - w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xe + w * _sin
        y = ye - w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xe - w * _sin
        y = ye + w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        points.append(points[0])
        obj.plane = Part.Face(Part.makePolygon(points))
        obj.solid = obj.plane.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))

    def get_new_points(self, obj):
        x1 = obj.start_point.x
        y1 = obj.start_point.y
        x2 = obj.end_point.x
        y2 = obj.end_point.y
        if obj.offset != 0:
            neg = False if obj.offset >= 0 else True
            distance = abs(obj.offset)
            x1, y1, x2, y2 = FrameObj.offset_frame_points(x1, y1, x2, y2, distance, neg)
        return x1, y1, x2, y2


class ViewProviderRectangle:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.LineColor = (1.00,0.00,0.00)
        # obj.addProperty("App::PropertyBool", "show_width", "display", "")

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "rectangle.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


if __name__ == "__main__":
    make_rectangle_slab(
            p1=FreeCAD.Vector(0, 0, 0),
            p2=FreeCAD.Vector(1, 1, 0),
            width = 5,
            height = 3,
               )
