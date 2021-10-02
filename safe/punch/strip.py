import math
from pathlib import Path
import Part
import FreeCAD


def make_strip(p1, p2, layer, design_type, swl, swr, ewl, ewr):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Strip")
    Strip(obj)
    obj.start_point = p1
    obj.end_point = p2
    obj.layer = layer
    obj.design_type = design_type
    obj.start_width_left = swl
    obj.start_width_right = swr
    obj.end_width_left = ewl
    obj.end_width_right = ewr
    if FreeCAD.GuiUp:
        ViewProviderStrip(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Strip:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        if not hasattr(obj, "start_point"):
            obj.addProperty(
                "App::PropertyVector",
                "start_point",
                "Geometry",
                )
        if not hasattr(obj, "end_point"):
            obj.addProperty(
                "App::PropertyVector",
                "end_point",
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
        if not hasattr(obj, "start_width_left"):
            obj.addProperty(
                "App::PropertyLength",
                "start_width_left",
                "Strip",
                )
        if not hasattr(obj, "start_width_right"):
            obj.addProperty(
                "App::PropertyLength",
                "start_width_right",
                "Strip",
                )
        if not hasattr(obj, "end_width_left"):
            obj.addProperty(
                "App::PropertyLength",
                "end_width_left",
                "Strip",
                )
        if not hasattr(obj, "end_width_right"):
            obj.addProperty(
                "App::PropertyLength",
                "end_width_right",
                "Strip",
                )
        if not hasattr(obj, "angle"):
            obj.addProperty(
            "App::PropertyAngle",
            "angle",
            "Strip",
            )
        
    def onChanged(self, obj, prop):
        return

    def execute(self, obj):
        v = obj.end_point - obj.start_point
        obj.angle = math.atan2(v.y, v.x)
        self.create_width(obj)
        if obj.layer == 'A':
            obj.ViewObject.ShapeColor = (1.00,0.00,0.00)
        elif obj.layer == 'B':
            obj.ViewObject.ShapeColor = (0.00,1.00,0.00)

    def create_width(self, obj):
        p1 = obj.start_point
        p2 = obj.end_point
        shapes = []
        shapes.append(Part.makeLine(p1, p2))
        points = []
        xs = obj.start_point.x
        ys = obj.start_point.y
        xe = obj.end_point.x
        ye = obj.end_point.y
        sl = obj.start_width_left.Value
        sr = obj.start_width_right.Value
        el = obj.end_width_left.Value
        er = obj.end_width_right.Value
        teta = obj.angle
        FreeCAD.Console.PrintMessage(f"teta = {teta}")
        _sin = math.sin(teta)
        _cos = math.cos(teta)
        x = xs - sl * _sin
        y = ys + sl * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xs + sr * _sin
        y = ys - sr * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xe + er * _sin
        y = ye - er * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xe - el * _sin
        y = ye + el * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        points.append(points[0])
        shapes.append(Part.Face(Part.makePolygon(points)))
        obj.Shape = Part.makeCompound(shapes)


class ViewProviderStrip:
    def __init__(self, vobj):
        vobj.Proxy = self        

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "strip.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


if __name__ == "__main__":
    make_strip(p1=FreeCAD.Vector(0, 16400, 0),
               p2=FreeCAD.Vector(12210, 16400, 0),
               layer='A',
               design_type='column',
               swl='25 cm',
               swr=250,
               ewl=250,
               ewr=250,
               )
