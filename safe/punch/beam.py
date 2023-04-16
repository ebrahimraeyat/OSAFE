import FreeCAD
import Draft
from safe.punch import punch_funcs


def make_beam(p1, p2):
    obj = Draft.make_line(p1, p2)
    obj.addProperty("App::PropertyString", "type").type = 'Beam'
    if FreeCAD.GuiUp:
        punch_funcs.format_view_object(
            obj=obj,
            shape_color_entity="beam_shape_color",
            line_width_entity="beam_line_width",
            transparency_entity="beam_transparency",
            display_mode_entity="beam_display_mode",
            line_color_entity="beam_line_color",
            )
        obj.ViewObject.PointSize = 4
    FreeCAD.ActiveDocument.recompute()
    return obj
