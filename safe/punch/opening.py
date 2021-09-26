from pathlib import Path
import Part
import FreeCAD
try:
    from safe.punch.punch_funcs import sort_vertex
except:
    from punch_funcs import sort_vertex


def make_opening(points, height=2000):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Opening")
    Opening(obj)
    obj.points = points
    obj.height = height
    if FreeCAD.GuiUp:
        _ViewProviderOpening(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Opening:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "opening"
        self.set_properties(obj)

    def set_properties(self, obj):
        if not hasattr(obj, "points"):
            obj.addProperty(
            "App::PropertyVectorList",
            "points",
            "Geometry",
            )
        if not hasattr(obj, "plane"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plane",
                "openning",
                )
        # if not hasattr(obj, "solid"):
        #     obj.addProperty(
        #         "Part::PropertyPartShape",
        #         "solid",
        #         "openning",
        #         )
        # if not hasattr(obj, "foundation"):
        #     obj.addProperty(
        #         "Part::PropertyLink",
        #         "foundation",
        #         "openning",
        #         )
        if not hasattr(obj, "height"):
            obj.addProperty(
            "App::PropertyLength",
            "height",
            "slab",
            )

    def onChanged(self, obj, prop):
        return

    def execute(self, obj):
        z = obj.points[0].z
        points_xy = sort_vertex([[p.x, p.y] for p in obj.points])
        points_vec = [FreeCAD.Vector(p[0], p[1], z) for p in points_xy]
    
        points = points_vec + [points_vec[0]]
        obj.plane = Part.Face(Part.makePolygon(points))
        obj.Shape = obj.plane.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))


class _ViewProviderOpening:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.Transparency = 95
        vobj.DisplayMode = "Shaded"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "opening.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


if __name__ == "__main__":
    x1 = 10
    x2 = 25
    y1 = 7
    y2 = 17
    p1=FreeCAD.Vector(x1, y1, 0)
    p2=FreeCAD.Vector(x2, y1, 0)
    p3=FreeCAD.Vector(x2, y2, 0)
    p4=FreeCAD.Vector(x1, y2, 0)
    points = [p1, p2, p3, p4]
    make_opening(
            points=points,
            height = 3,
               )
