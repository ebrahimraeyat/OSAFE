from pathlib import Path
import Part
import FreeCAD
import Sketcher
import ArchComponent


def make_slab(
        base,
        height=1000,
        ks = None,
        fc = None,
        ):
    doc = FreeCAD.ActiveDocument
    obj = doc.addObject("Part::FeaturePython", "Slab")
    Slab(obj)
    obj.Base = base
    obj.height = height
    if ks is not None:
        obj.ks = ks
    if fc is not None:
        obj.fc = fc
    if FreeCAD.GuiUp:
        ViewProviderSlab(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class Slab(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Footing"
        self.set_properties(obj)
        obj.Proxy = self

    def set_properties(self, obj):
        if not hasattr(obj, "height"):
            obj.addProperty(
            "App::PropertyLength",
            "height",
            "Base",
            )
        if not hasattr(obj, "ks"):
            obj.addProperty(
            "App::PropertyFloat",
            "ks",
            "Soil",
            )
        if not hasattr(obj, "fc"):
            obj.addProperty(
            "App::PropertyPressure",
            "fc",
            "Concrete",
            )
        

    def onDocumentRestored(self, obj):
        obj.Proxy = self
        super().onDocumentRestored(obj)
        self.set_properties(obj)

    def execute(self, obj):
        if hasattr(obj, "Base") and obj.Base:
            wire = obj.Base.Shape.Wires[0]
            plan = Part.Face(wire)
            obj.Shape = plan.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))


class ViewProviderSlab:
    def __init__(self, vobj):
        vobj.Proxy = self
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
        return str(Path(__file__).parent / "Resources" / "icons" / "slab.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


if __name__ == "__main__":
    import FreeCADGui as Gui
    sel = Gui.Selection.getSelection()
    if sel:
        wire = sel[0]
    else:
        x1 = 0
        x2 = 2500
        y1 = 0
        y2 = 1700
        p1=FreeCAD.Vector(x1, y1, 0)
        p2=FreeCAD.Vector(x2, y1, 0)
        p3=FreeCAD.Vector(x2, y2, 0)
        p4=FreeCAD.Vector(x1, y2, 0)
        points = [p1, p2, p3, p4, p1]
        import Draft
        wire = Draft.make_wire(points)
    make_slab(base=wire,
               )
