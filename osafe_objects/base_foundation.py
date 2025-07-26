from pathlib import Path
from typing import Union
import FreeCAD
import ArchComponent

from osafe_funcs import osafe_funcs

if FreeCAD.GuiUp:
    import FreeCADGui as Gui
    from osafe_py_widgets import resource_rc


def make_base_foundation(
        base,
        layer : str = 'A',
        width : float = 1000,
        height : float = 1000,
        soil_modulus : float =2,
        fc : Union[float, str] = '25 MPa',
        align : str = 'Center',
        left_width : Union[float, bool] = None,
        right_width : Union[float, bool] = None,
        design_type : str = 'column',
        ):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "BaseFoundation")
    BaseFoundation(obj)
    obj.Base = base
    obj.layer = layer
    obj.design_type = design_type
    obj.width = width
    if align == 'Left':
        obj.left_width = left_width
        obj.right_width = width - left_width
    elif align == 'Right':
        obj.right_width = right_width
        obj.left_width = width - right_width
    elif align == 'Center':
        obj.left_width = obj.right_width = obj.width / 2
    obj.align = align
    obj.height = height
    obj.setExpression('ks', f'{soil_modulus} * width.Value / width.Value')
    obj.fc = fc
    if FreeCAD.GuiUp:
        vobj = obj.ViewObject
        ViewProviderBaseFoundation(vobj)
    FreeCAD.ActiveDocument.recompute()
    return obj


class BaseFoundation(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Footing"
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "BaseFoundation"
        obj.Proxy = self
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
        if not hasattr(obj, "ks"):
            obj.addProperty(
                "App::PropertyFloat",
                "ks",
                "Soil",
                )
        if not hasattr(obj, "left_width"):
            obj.addProperty(
                "App::PropertyLength",
                "left_width",
                "Geometry",
                ).left_width = '0.5 m'
        if not hasattr(obj, "right_width"):
            obj.addProperty(
                "App::PropertyLength",
                "right_width",
                "Geometry",
                ).right_width = '0.5 m'
        if not hasattr(obj, "width"):
            obj.addProperty(
                "App::PropertyLength",
                "width",
                "Geometry",
                ).width = '1 m'
        if not hasattr(obj, "height"):
            obj.addProperty(
                "App::PropertyLength",
                "height",
                "Slab",
                ).height = '1 m'
        if not hasattr(obj, "align"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "align",
                "Geometry",
                ).align = ['Center', 'Left', 'Right']
        if not hasattr(obj, "extended_shape"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_shape",
                "Geometry",
                )
        if not hasattr(obj, "extended_first_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_first_edge",
                "Geometry",
                )
        if not hasattr(obj, "extended_last_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_last_edge",
                "Geometry",
                )
        if not hasattr(obj, "first_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "first_edge",
                "Geometry",
                )
        if not hasattr(obj, "last_edge"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "last_edge",
                "Geometry",
                )
        if not hasattr(obj, "plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "plan",
                "Geometry",
                )
        if not hasattr(obj, "extended_plan"):
            obj.addProperty(
                "Part::PropertyPartShape",
                "extended_plan",
                "Geometry",
                )
        if not hasattr(obj, "final_wire_first_point"):
            obj.addProperty(
                "App::PropertyVector",
                "final_wire_first_point",
                "Geometry",
                )
        if not hasattr(obj, "final_wire_last_point"):
            obj.addProperty(
                "App::PropertyVector",
                "final_wire_last_point",
                "Geometry",
                )
        if not hasattr(obj, "fc"):
            obj.addProperty(
            "App::PropertyPressure",
            "fc",
            "Concrete",
            )
        obj.setEditorMode('final_wire_first_point', 2)
        obj.setEditorMode('final_wire_last_point', 2)

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        self.set_properties(obj)

    def execute(self, obj):
        if obj.width.Value == 0:
            return
        if obj.layer == 'A':
            osafe_funcs.format_view_object(
            obj=obj,
            shape_color_entity="base_foundation_a_shape_color",
            line_width_entity="base_foundation_a_line_width",
            transparency_entity="base_foundation_a_transparency",
            display_mode_entity="base_foundation_a_display_mode",
            line_color_entity="base_foundation_a_line_color",
            )
        elif obj.layer == 'B':
            osafe_funcs.format_view_object(
            obj=obj,
            shape_color_entity="base_foundation_b_shape_color",
            line_width_entity="base_foundation_a_line_width",
            transparency_entity="base_foundation_a_transparency",
            display_mode_entity="base_foundation_a_display_mode",
            line_color_entity="base_foundation_b_line_color",
            )
        elif obj.layer == 'other':
            osafe_funcs.format_view_object(
            obj=obj,
            shape_color_entity="base_foundation_b_shape_color",
            line_width_entity="base_foundation_a_line_width",
            transparency_entity="base_foundation_a_transparency",
            display_mode_entity="base_foundation_a_display_mode",
            line_color_entity="base_foundation_b_line_color",
            )
            color = (0.20,1.00,0.00)
            obj.ViewObject.ShapeColor = obj.ViewObject.LineColor = color
        obj.Base.ViewObject.LineColor = obj.ViewObject.LineColor
        obj.Base.ViewObject.PointColor = obj.ViewObject.PointColor
        obj.Base.ViewObject.LineWidth = 3.00
        if obj.align == 'Left':
            sl = obj.left_width.Value
            sr = obj.width.Value - sl
            obj.right_width = sr
        elif obj.align == 'Right':
            sr = obj.right_width.Value
            sl = obj.width.Value - sr
            obj.left_width = sl
        elif obj.align == 'Center':
            sr = sl = obj.width.Value / 2
            obj.right_width = sr
            obj.left_width = sl

        obj.plan, _, _ = osafe_funcs.get_left_right_offset_wire_and_shape(obj.Base.Shape, sl, sr)
        obj.Shape = obj.plan.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))
        extended_main_wire, e1, e2 = osafe_funcs.get_extended_wire(obj.Base.Shape.Wires[0])
        obj.extended_first_edge = e1
        obj.extended_last_edge = e2
        obj.extended_shape, *_ = osafe_funcs.get_left_right_offset_wire_and_shape(extended_main_wire, sl, sr)


class ViewProviderBaseFoundation:
    def __init__(self, vobj):
        vobj.Proxy = self
        
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children = [self.Object.Base]
        return children

    def getIcon(self):
        return str(Path(__file__).parent.parent / "osafe_images" / "base_foundation.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
    def setEdit(self, vobj, mode=0):
        obj = vobj.Object
        ui = Ui(obj)
        Gui.Control.showDialog(ui)
        return True
    
    def unsetEdit(self, vobj, mode):
        Gui.Control.closeDialog()
        return
        
    def doubleClicked(self,vobj):
        self.setEdit(vobj)

    def onDelete(self, vobj, subelements):
        name = None
        if vobj.Object.Base:
            name = vobj.Object.Base.Name
        FreeCAD.ActiveDocument.removeObject(vobj.Object.Name)
        if name is not None:
            FreeCAD.ActiveDocument.removeObject(name)

class Ui:
    def __init__(self, obj=None):
        self.form = Gui.PySideUic.loadUi(str(Path(__file__).parent.parent / "osafe_widgets" / "edit_objects" / "edit_base_foundation.ui"))
        self.obj = obj
        self.original_values = self.fill_form()
        self.obj.ViewObject.Visibility = True
        self.align_changed()
        self.create_connections()

    def create_connections(self):
        self.form.strip_layer.currentIndexChanged.connect(self.modify_obj)
        self.form.align.currentIndexChanged.connect(self.align_changed)
        self.form.width_spinbox.valueChanged.connect(self.width_changed)
        self.form.left_width_spinbox.valueChanged.connect(self.width_changed)
        self.form.right_width_spinbox.valueChanged.connect(self.width_changed)
        self.form.accept_pushbutton.clicked.connect(self.accept)
        self.form.cancel_pushbutton.clicked.connect(self.reject)

    def align_changed(self):
        align = self.form.align.currentText()
        if align.lower() == 'center':
            self.form.left_width_spinbox.setEnabled(False)
            self.form.right_width_spinbox.setEnabled(False)
        elif align.lower() == 'left':
            self.form.left_width_spinbox.setEnabled(True)
            self.form.right_width_spinbox.setEnabled(False)
        elif align.lower() == 'right':
            self.form.left_width_spinbox.setEnabled(False)
            self.form.right_width_spinbox.setEnabled(True)
        self.modify_obj()

    def width_changed(self):
        bf_width = self.form.width_spinbox.value() * 10
        align = self.form.align.currentText()
        if align == 'Left':
            sl = self.form.left_width_spinbox.value() * 10
            sr = bf_width - sl
        elif align == 'Right':
            sr = self.form.right_width_spinbox.value() * 10
            sl = bf_width - sr
        elif align == 'Center':
            sr = sl = bf_width / 2
        self.form.left_width_spinbox.setValue(int(sl / 10))
        self.form.right_width_spinbox.setValue(int(sr / 10))
        self.modify_obj()

    def fill_form(self):
        layer = self.obj.layer
        index = self.form.strip_layer.findText(layer)
        self.form.strip_layer.setCurrentIndex(index)
        # align
        align = self.obj.align
        index = self.form.align.findText(align)
        self.form.align.setCurrentIndex(index)
        # width spinbox
        width = self.obj.width.Value
        self.form.width_spinbox.setValue(width / 10)
        # left width spinbox
        left_width = self.obj.left_width.Value
        self.form.left_width_spinbox.setValue(left_width / 10)
        # right width spinbox
        right_width = self.obj.right_width.Value
        self.form.right_width_spinbox.setValue(right_width / 10)
        return {
        "layer": layer,
        "align": align,
        "width": width,
        "left_width": left_width,
        "right_width": right_width,
        "visibility": self.obj.ViewObject.Visibility,
        }

    def accept(self):
        self.obj.ViewObject.Visibility = self.original_values["visibility"]
        FreeCAD.ActiveDocument.recompute()
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def reject(self):
        self.obj.layer = self.original_values["layer"]
        self.obj.align = self.original_values["align"]
        self.obj.width = self.original_values["width"]
        self.obj.left_width = self.original_values["left_width"]
        self.obj.right_width = self.original_values["right_width"]
        self.obj.ViewObject.Visibility = self.original_values["visibility"]
        self.obj.recompute(True)
        Gui.Control.closeDialog()

    def modify_obj(self):
        self.obj.layer = self.form.strip_layer.currentText()
        self.obj.align = self.form.align.currentText()
        self.obj.width = self.form.width_spinbox.value() * 10
        self.obj.left_width = self.form.left_width_spinbox.value() * 10
        self.obj.right_width = self.form.right_width_spinbox.value() * 10
        self.obj.recompute(True)


if __name__ == "__main__":
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1000, 0, 0)
    p3 = FreeCAD.Vector(3000, 2000, 0)
    import Draft
    wire = Draft.make_wire([p1, p2, p3])
    make_base_foundation(
            base=wire,
            layer='other',
            design_type='column',
            )
