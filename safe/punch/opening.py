from pathlib import Path
import Part
import FreeCAD
import Sketcher
import ArchComponent

try:
    from safe.punch import punch_funcs
except:
    import punch_funcs


def make_opening(points, height=2000):
    z = points[0].z
    doc = FreeCAD.ActiveDocument
    obj = doc.addObject("Part::FeaturePython", "Opening")
    Opening(obj)
    sketch = doc.addObject('Sketcher::SketchObject', 'sketch')
    sketch.Placement.Base.z = z
    points_xy = punch_funcs.sort_vertex([[p.x, p.y] for p in points])
    points_vec = [FreeCAD.Vector(p[0], p[1], 0) for p in points_xy]
    points = points_vec + [points_vec[0]]
    sketch_lines = []
    for p1, p2 in zip(points[:-1], points[1:]):
        sketch_lines.append(sketch.addGeometry(Part.LineSegment(p1, p2)))
    for l1, l2 in zip(sketch_lines[:-1], sketch_lines[1:]):
        sketch.addConstraint(Sketcher.Constraint('Coincident', l1, 2, l2, 1))
    sketch.addConstraint(Sketcher.Constraint('Coincident', sketch_lines[-1], 2, sketch_lines[0], 1))
    obj.Base = sketch
    # sketch.ViewObject.Visibility = False
    obj.ViewObject.Visibility = False
    obj.height = height
    
    if FreeCAD.GuiUp:
        _ViewProviderOpening(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Opening(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Opening Element"
        self.set_properties(obj)
        obj.Proxy = self

    def set_properties(self, obj):
        if not hasattr(obj, "plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan",
                "opening",
                )
        # if not hasattr(obj, "solid"):
        #     obj.addProperty(
        #         "Part::PropertyPartShape",
        #         "solid",
        #         "opening",
        #         )
        if not hasattr(obj, "height"):
            obj.addProperty(
            "App::PropertyLength",
            "height",
            "Base",
            )

    def onDocumentRestored(self, obj):
        obj.Proxy = self
        super().onDocumentRestored(obj)
        self.set_properties(obj)

    def execute(self, obj):
        if hasattr(obj, "Base") and obj.Base:
            wire = obj.Base.Shape.Wires[0]
            obj.plan = Part.Face(wire)
            points = punch_funcs.get_sort_points(
                wire.Edges,
                sort_edges=True,
            )
            # lines = []
            # for p1, p2 in zip(points[:-2], points[2:]):
            #     lines.append(Part.makeLine(p1, p2))
            
            shape = obj.plan.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
            # obj.Shape = Part.makeCompound([shape] + lines)
            obj.Shape = shape


class _ViewProviderOpening:
    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.Transparency = 70
        vobj.ShapeColor = (0.00,1.00,1.00)
        vobj.DisplayMode = "Shaded"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = [FreeCAD.ActiveDocument.getObject(self.Object.Base.Name)]
        return children

    # def onDelete(self, vobj, subelements):
    #     FreeCAD.ActiveDocument.removeObject(self.Object.Base.Name)

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "opening.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


if __name__ == "__main__":
    x1 = 10
    x2 = 2500
    y1 = 7
    y2 = 1700
    p1=FreeCAD.Vector(x1, y1, 0)
    p2=FreeCAD.Vector(x2, y1, 0)
    p3=FreeCAD.Vector(x2, y2, 0)
    p4=FreeCAD.Vector(x1, y2, 0)
    points = [p1, p2, p3, p4]
    make_opening(
            points=points,
            # height = 3,
               )
