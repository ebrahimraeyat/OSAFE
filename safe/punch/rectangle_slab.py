import math
from pathlib import Path
import Part
import FreeCAD
from etabs_api.frame_obj import FrameObj
from safe.punch import punch_funcs
from safe.punch.strip import make_strip


def make_rectangle_slab(p1, p2, width=1, height=1, offset=0):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Slab")
    RectangleSlab(obj)
    obj.start_point = p1
    obj.end_point = p2
    obj.width = width
    obj.height = height
    obj.offset = offset
    # swl = ewl = width / 2 + offset
    # swr = ewr = width / 2 - offset
    # dx = abs(p1.x - p2.x)
    # dy = abs(p1.y - p2.y)
    # if dx > dy:
    #     layer = 'A'
    # else:
    #     layer = 'B'
    # strip = make_strip(p1, p2, layer, 'column',
    #     swl, swr, ewl, ewr)
    # obj.strip = strip
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
        if not hasattr(obj, "points"):
            obj.addProperty(
                "App::PropertyVectorList",
                "points",
                "slab",
                )
        if not hasattr(obj, "extend"):
            obj.addProperty(
            "App::PropertyLength",
            "extend",
            "slab",
            ).extend = 3000
        # if not hasattr(obj, "strip"):
        #     obj.addProperty(
        #         "App::PropertyLink",
        #         "strip",
        #         "slab",
        #         )

    def onChanged(self, obj, prop):
        return

    def execute(self, obj):
        p1 = obj.start_point
        p2 = obj.end_point
        obj.Shape = Part.makeLine(p1, p2)
        v = p2 - p1
        obj.angle = math.atan2(v.y, v.x)
        self.create_width(obj)
        # if hasattr(obj, 'strip') and obj.strip is not None:
        #     obj.strip.start_point = obj.start_point
        #     obj.strip.end_point = obj.end_point
        #     obj.strip.angle = obj.angle
        #     swl = ewl = obj.width.Value / 2 + obj.offset
        #     swr = ewr = obj.width.Value / 2 - obj.offset
        #     obj.strip.start_width_left = swl
        #     obj.strip.start_width_right = swr
        #     obj.strip.end_width_left = ewl
        #     obj.strip.end_width_right = ewr

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
        obj.points = points
        points.append(points[0])
        obj.plane = Part.Face(Part.makePolygon(points))
        obj.solid = obj.plane.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))

    def get_new_points(self, obj):
        p1 = obj.start_point
        p2 = obj.end_point
        xs = p1.x
        xe = p2.x
        delta_x = xe - xs
        d = p1.distanceToPoint(p2)
        if delta_x == 0:
            dx = 0
            dy = obj.extend.Value
            new_start_point = p1.add(FreeCAD.Vector(dx, -dy, 0))
            new_d = new_start_point.distanceToPoint(p2)
            if new_d > d:
                new_end_point = p2.add(FreeCAD.Vector(dx, dy, 0))
            else:
                new_start_point = p1.add(FreeCAD.Vector(dx, dy, 0))
                new_end_point = p2.add(FreeCAD.Vector(dx, -dy, 0))
        else:
            new_start_point, new_end_point = punch_funcs.extend_two_points(p1, p2, obj.extend.Value)
        x1 = new_start_point.x
        y1 = new_start_point.y
        x2 = new_end_point.x
        y2 = new_end_point.y
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

    # def claimChildren(self):
    #     o = self.Object.strip
    #     if o is not None:
    #         children=[FreeCAD.ActiveDocument.getObject(o.Name)]
    #         return children
    #     return []


if __name__ == "__main__":
    make_rectangle_slab(
            p1=FreeCAD.Vector(0, 0, 0),
            p2=FreeCAD.Vector(1000, 1000, 0),
            width = 200,
            height = 200,
               )
