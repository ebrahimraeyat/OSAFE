from pathlib import Path
from typing import Union

import FreeCAD
import FreeCADGui
import Part


class Foundation:
    def __init__(self, obj):
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "Foundation"
        obj.Proxy = self

        if not hasattr(obj, "fc"):
            obj.addProperty(
                "App::PropertyPressure",
                "fc",
                "Concrete",
                )

        if not hasattr(obj, "height"):
            obj.addProperty(
                "App::PropertyLength",
                "height",
                "Foundation",
                )

        if not hasattr(obj, "cover"):
            obj.addProperty(
                "App::PropertyLength",
                "cover",
                "Foundation",
                )

        if not hasattr(obj, "d"):
            obj.addProperty(
                "App::PropertyLength",
                "d",
                "Foundation",
                )

        if not hasattr(obj, "plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan",
                "Foundation",
                )

        obj.setEditorMode("d", 2)

    def onDocumentRestored(self, obj):
        self.set_properties(obj)

    def execute(self, obj):
        obj.d = obj.height - obj.cover
        sh = obj.plan.extrude(FreeCAD.Vector(0, 0, -(obj.d.Value)))
        obj.Shape = sh


class ViewProviderFoundation:

    def __init__(self, vobj):

        vobj.Proxy = self
        vobj.Transparency = 40
        vobj.DisplayMode = "Shaded"


    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return str(Path(__file__).parent.parent / "osafe_images" / "foundation.png")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None



def make_foundation(
    base: Part.Shape = None,
    height: Union[float, str] = 1000,
    cover: Union[float, str] = 75,
    fc: Union[float, str] = 25
    ):
    if not base:
        base = FreeCADGui.Selection.getSelection()[0].Shape

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
    Foundation(obj)
    ViewProviderFoundation(obj.ViewObject)
    obj.plan = base
    obj.height = height
    obj.cover = cover
    obj.fc = f"{fc} MPa"

    FreeCAD.ActiveDocument.recompute()

    return obj




        