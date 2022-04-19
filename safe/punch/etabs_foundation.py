from os.path import join, dirname, abspath
from typing import Union

from PySide2 import QtCore
import FreeCAD
import Part
import ArchComponent

try:
    from safe.punch import punch_funcs
except:
    import punch_funcs


class Foundation(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Footing"
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "Foundation"
        obj.Proxy = self
        self.obj_name = obj.Name

        if not hasattr(obj, "fc"):
            obj.addProperty(
                "App::PropertyPressure",
                "fc",
                "Foundation",
                )

        if not hasattr(obj, "height"):
            obj.addProperty(
                "App::PropertyLength",
                "height",
                "Geometry",
                )

        if not hasattr(obj, "cover"):
            obj.addProperty(
                "App::PropertyLength",
                "cover",
                "Geometry",
                )
        if not hasattr(obj, "d"):
            obj.addProperty(
                "App::PropertyLength",
                "d",
                "Geometry",
                )

        if not hasattr(obj, "base_foundations"):
            obj.addProperty(
                "App::PropertyLinkList",
                "base_foundations",
                "Foundation",
                )

        if not hasattr(obj, "plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan",
                "Foundation",
                )
        if not hasattr(obj, "plan_without_openings"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan_without_openings",
                "Foundation",
                )
        if not hasattr(obj, "outer_wire"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "outer_wire",
                "Foundation",
                )
        if not hasattr(obj, "openings"):
            obj.addProperty(
                "App::PropertyLinkList",
                "openings",
                "Foundation",
                )
        if not hasattr(obj, "split"):
        	obj.addProperty(
        		"App::PropertyBool",
        		"split",
        		"Mat",
        		).split = True
        if not hasattr(obj, "foundation_type"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "foundation_type",
                "Foundation",
                ).foundation_type = ['Strip', 'Mat']
        if not hasattr(obj, "continuous_layer"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "continuous_layer",
                "Strip",
                ).continuous_layer = ['A', 'B', 'AB']
        # if not hasattr(obj, "loadcases"):
        # 	obj.addProperty(
        # 		"App::PropertyStringList",
        # 		"loadcases",
        # 		"Loads",
        # 		)
        if not hasattr(obj, "level"):
            obj.addProperty(
                "App::PropertyDistance",
                "level",
                "Foundation",
            )
        if not hasattr(obj, "redraw"):
            obj.addProperty(
                "App::PropertyBool",
                "redraw",
                "Foundation",
                ).redraw = False
        obj.setEditorMode('redraw', 2)
        obj.setEditorMode('level', 2)
        obj.setEditorMode('d', 1)

    def execute(self, obj):
        if obj.redraw:
            obj.redraw = False
            return
        QtCore.QTimer().singleShot(50, self._execute)

    def _execute(self):
        obj = FreeCAD.ActiveDocument.getObject(self.obj_name)
        obj.d = obj.height - obj.cover
        if not obj:
            FreeCAD.ActiveDocument.recompute()
            return
        obj.redraw = True
        obj.Shape, obj.outer_wire, obj.plan, obj.plan_without_openings = punch_funcs.get_foundation_shape_from_base_foundations(
                obj.base_foundations,
                height = obj.height.Value,
                foundation_type = obj.foundation_type,
                continuous_layer = obj.continuous_layer,
                openings=obj.openings,
                split_mat=obj.split,
                )
            
        
        # obj.plan, obj.plan_without_openings, holes = punch_funcs.get_foundation_plan_with_holes(obj)
        # obj.Shape = obj.plan.copy().extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
        # for i, face in enumerate(obj.Shape.Faces, start=1):
        # 	if face.BoundBox.ZLength == 0 and face.BoundBox.ZMax == obj.level.Value:
        # 		obj.top_face = f'Face{i}'
        # for o in doc.Objects:
        # 	if (
        # 		hasattr(o, 'TypeId') and
        # 		o.TypeId == 'Fem::ConstraintForce'
        # 		):
        # 		o.References = [obj, obj.top_face]
        # obj.d = obj.height - obj.cover
        FreeCAD.ActiveDocument.recompute()

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        self.set_properties(obj)
        obj.redraw = False
        
class ViewProviderFoundation:

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return join(dirname(abspath(__file__)), "Resources", "icons","foundation.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def claimChildren(self):
        children=[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.base_foundations] + \
                [FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.openings]
        return children

def make_foundation(
    cover: float = 75,
    fc: int = 25,
    height : int = 800,
    foundation_type : str = 'Strip',
    # load_cases : list = [],
    base_foundations : Union[list, None] = None,
    continuous_layer : str = 'A',
    ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
    Foundation(obj)
    if FreeCAD.GuiUp:
        import FreeCADGui
        ViewProviderFoundation(obj.ViewObject)
        obj.ViewObject.LineWidth = 1.00
        obj.ViewObject.PointSize = 1.00
        obj.ViewObject.DisplayMode = "Flat Lines"
        obj.ViewObject.ShapeColor = (1.00,0.67,0.50)
        obj.ViewObject.LineColor = (0.28,0.28,0.28)
        obj.ViewObject.PointColor = (0.28,0.28,0.28)
        FreeCADGui.activeDocument().activeView().viewIsometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")
    obj.cover = cover
    obj.fc = f"{fc} MPa"
    obj.height = height
    obj.d = height - cover
    obj.foundation_type = foundation_type
    if base_foundations is None:
        base_foundations = []
        for o in FreeCAD.ActiveDocument.Objects:
            if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
                base_foundations.append(o)
    obj.level = base_foundations[0].Base.Placement.Base.z
    obj.base_foundations = base_foundations
    obj.continuous_layer = continuous_layer
    FreeCAD.ActiveDocument.recompute()
    return obj


if __name__ == '__main__':
    make_foundation()

        