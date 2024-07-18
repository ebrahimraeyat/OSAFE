from typing import Union
from pathlib import Path

from PySide2 import QtCore
import FreeCAD
import FreeCADGui
# import Part
import ArchComponent

try:
    from osafe_funcs import osafe_funcs
except:
    import osafe_funcs

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
                "",
                # 8,
                )
        if not hasattr(obj, "ks"):
            obj.addProperty(
                "App::PropertyFloat",
                "ks",
                "Soil",
                "",
                8,
                )

        if not hasattr(obj, "height"):
            obj.addProperty(
                "App::PropertyLength",
                "height",
                "Geometry",
                )
        if not hasattr(obj, "volume"):
            obj.addProperty(
                "App::PropertyFloat",
                "volume",
                "Foundation",
                )
        
        if not hasattr(obj, "height_punch"):
            obj.addProperty(
                "App::PropertyLength",
                "height_punch",
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

        if not hasattr(obj, "Slabs"):
            obj.addProperty(
                "App::PropertyLinkList",
                "Slabs",
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
        if not hasattr(obj, "tolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "tolerance",
                "Foundation",
                )
        obj.setEditorMode('redraw', 2)
        obj.setEditorMode('level', 2)
        obj.setEditorMode('d', 1)

    def onChanged(self, obj, prop):
        """Execute when a property is changed."""
        if prop == 'height' and obj.height != 0 and hasattr(obj, 'height_punch'):
            obj.height_punch = obj.height

    def execute(self, obj):
        if obj.redraw:
            obj.redraw = False
            return
        QtCore.QTimer().singleShot(50, self._execute)

    def _execute(self):
        obj = FreeCAD.ActiveDocument.getObject(self.obj_name)
        if obj.height == 0:
            obj.d = obj.height_punch - obj.cover
        else:
            obj.d = obj.height - obj.cover
        if not obj:
            FreeCAD.ActiveDocument.recompute()
            return
        obj.redraw = True
        obj.Shape, obj.outer_wire, obj.plan, obj.plan_without_openings = osafe_funcs.get_foundation_shape_from_base_foundations(
                obj.base_foundations,
                height = obj.height.Value,
                foundation_type = obj.foundation_type,
                continuous_layer = obj.continuous_layer,
                openings=obj.openings,
                split_mat=obj.split,
                slabs=obj.Slabs,
                tol=obj.tolerance,
                )
        # obj.plan, obj.plan_without_openings, holes = osafe_funcs.get_foundation_plan_with_holes(obj)
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
        obj.volume = obj.Shape.Volume / 1e9
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
        return str(Path(__file__).parent.parent / "osafe_images" / "foundation.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def claimChildren(self):
        children=self.Object.base_foundations + \
                self.Object.Slabs + \
                self.Object.openings
        return children

    def setupContextMenu(self, vobj, menu):
        from PySide2 import QtGui, QtWidgets
        icon_path = str(
                Path(__file__).parent.absolute() / "osafe_images" / "explode_foundation.svg"
                )
        icon = QtGui.QIcon(icon_path)
        action1 = QtWidgets.QAction(icon,"Explode Foundation", menu)
        action1.triggered.connect(explode_foundation)
        menu.addAction(action1)

def explode_foundation():
    FreeCADGui.runCommand('osafe_explode_foundation')

def make_foundation(
    cover: float = 75,
    fc: int = 25,
    height : int = 800,
    foundation_type : str = 'Strip',
    # load_cases : list = [],
    base_foundations : Union[list, None] = None,
    continuous_layer : str = 'AB',
    ks : float = 2,
    openings : list = [],
    tol : float = 0,
    ):
    from draftutils.translate import translate
    FreeCAD.ActiveDocument.openTransaction(translate("OSAFE","Make Foundation"))
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
    # obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", "Foundation")
    Foundation(obj)
    if FreeCAD.GuiUp:
        import FreeCADGui
        ViewProviderFoundation(obj.ViewObject)
        osafe_funcs.format_view_object(
            obj=obj,
            shape_color_entity="foundation_shape_color",
            line_width_entity="foundation_line_width",
            transparency_entity="foundation_transparency",
            display_mode_entity="foundation_display_mode",
            line_color_entity="foundation_line_color",
            )
        FreeCADGui.activeDocument().activeView().viewIsometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")
    obj.cover = cover
    obj.tolerance = tol
    obj.fc = f"{fc} MPa"
    obj.ks = ks
    obj.height = height
    obj.d = height - cover
    obj.foundation_type = foundation_type
    if base_foundations is None:
        base_foundations = []
        for o in FreeCAD.ActiveDocument.Objects:
            if hasattr(o, 'Proxy') and hasattr(o.Proxy, 'Type') and o.Proxy.Type == 'BaseFoundation':
                base_foundations.append(o)
    if height == 0:
        obj.height_punch = base_foundations[0].height
    else:
        obj.height_punch = height
    obj.level = base_foundations[0].Base.Placement.Base.z
    obj.base_foundations = base_foundations
    obj.continuous_layer = continuous_layer
    obj.openings = openings
    # obj.shape, obj.outer_wire, obj.plan, obj.plan_without_openings = osafe_funcs.get_foundation_shape_from_base_foundations(
    #             base_foundations,
    #             height = obj.height.Value,
    #             foundation_type = obj.foundation_type,
    #             continuous_layer = obj.continuous_layer,
    #             openings=obj.openings,
    #             split_mat=obj.split,
    #             )
    # obj.Group = obj.Slabs
    # for slab in obj.Slabs:
    #     if slab.Proxy.Type == "Slab":
    #         slab.fc = obj.fc
    if FreeCAD.GuiUp:
        for bf in base_foundations:
            show_object(bf, False)
            show_object(bf.Base, False)
    FreeCAD.ActiveDocument.commitTransaction()
    FreeCAD.ActiveDocument.recompute()
    return obj

def show_object(obj, show : bool = True):
    if show:
        obj.ViewObject.show()
    else:
        obj.ViewObject.hide()


if __name__ == '__main__':
    make_foundation()

        