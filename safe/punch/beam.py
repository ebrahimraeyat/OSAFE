from pathlib import Path

from numpy import void
import Part
import FreeCAD


def make_beam(p1, p2):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Beam")
    Beam(obj)
    obj.start_point = p1
    obj.end_point = p2
    if FreeCAD.GuiUp:
        vobj = obj.ViewObject
        ViewProviderBeam(vobj)
        vobj.LineWidth = 3
        vobj.PointSize = 6
        vobj.LineColor = (1., 1., 0.)
        vobj.PointColor = (1., 1., 0.)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Beam:
    def __init__(self, obj):
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.Proxy = self
        self.Type = "Beam"
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

    def execute(self, obj):
        p1 = obj.start_point
        p2 = obj.end_point
        obj.Shape = Part.makeLine(p1, p2)


class ViewProviderBeam:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "beam.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

if __name__ == "__main__":
    make_beam(
            p1=FreeCAD.Vector(0, 0, 0),
            p2=FreeCAD.Vector(1000, 1000, 0),
               )
