from typing import Union
from pathlib import Path

import FreeCAD


class SafeF2k:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "f2k"
        self.set_properties(obj)

    def set_properties(self, obj):

        if not hasattr(obj, "input"):
            obj.addProperty(
                "App::PropertyFile",
                "input",
                "Safe",
                )
        if not hasattr(obj, "output"):
            obj.addProperty(
                "App::PropertyFile",
                "output",
                "Safe",
                )

    def onDocumentRestored(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

class ViewProviderF2k:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return str(Path(__file__).parent / "Resources" / "icons" / "f2k.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

def make_safe_f2k(
    input : str,
    output : Union[str, None] = None,
    ):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Safe")
    SafeF2k(obj)
    obj.input = input
    if not output is None:
        obj.output = output
    if FreeCAD.GuiUp:
        ViewProviderF2k(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj




		