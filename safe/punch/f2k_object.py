from typing import Union
from pathlib import Path

import FreeCAD


class SafeF2k:
    def __init__(self, obj):
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "f2k"
        obj.Proxy = self

        if not hasattr(obj, "input"):
            obj.addProperty(
                "App::PropertyFile",
                "input",
                "Safe",
                )
        if not hasattr(obj, "input_str"):
            obj.addProperty(
                "App::PropertyString",
                "input_str",
                "Safe",
                ).input_str=''
        if not hasattr(obj, "output"):
            obj.addProperty(
                "App::PropertyFile",
                "output",
                "Safe",
                )
        obj.setEditorMode('output', 1)
        obj.setEditorMode('input_str', 2)

    def execute(self, obj):
        input_ = obj.input
        obj.input = input_.replace('/', '\\')
        output = obj.output
        obj.output = output.replace('/', '\\')
        try:
            if Path(obj.input).exists():
                with open(obj.input) as f:
                    obj.input_str = f.read()
        except:
            pass

    def onDocumentRestored(self, obj):
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
    input : str='',
    output : Union[str, None] = None,
    ):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Safe")
    SafeF2k(obj)
    obj.input = input
    if output is not None:
        obj.output = output
    if FreeCAD.GuiUp:
        ViewProviderF2k(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj




		