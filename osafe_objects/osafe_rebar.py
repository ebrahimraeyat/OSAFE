#***************************************************************************
#*   Copyright (c) 2013 Yorik van Havre <yorik@uncreated.net>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************
# Modified Amritpal Singh <amrit3701@gmail.com> on 07-07-2017
# Modified Ebrahim Raeyat <ebe79442114@gmail.com> on 03-01-2024
from pathlib import Path

import FreeCAD
import Part
import ArchComponent
import ArchCommands
if FreeCAD.GuiUp:
    import FreeCADGui as Gui
    from draftutils.translate import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    
from osafe_funcs import osafe_funcs as osf

app_prop = "App::Property"
prop_length = "App::PropertyLength"
prop_dist = "App::PropertyDistance"
prop_float = "App::PropertyFloat"
prop_string = "App::PropertyString"
prop_integer = "App::PropertyInteger"
prop_link = "App::PropertyLink"

def make_rebars(
        top_rebar_diameter: int=20,
        bot_rebar_diameter: int=20,
        stirrup_diameter: int=12,
        extended: float=0,
        min_ratio_of_rebars: float=0.0018,
        ):
    doc = FreeCAD.ActiveDocument
    if not doc:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return
    rebars = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Rebars")
    for strip in doc.Objects:
        if hasattr(strip, "Proxy") and hasattr(strip.Proxy, "Type") and strip.Proxy.Type == "Strip":
            obj = doc.addObject("Part::FeaturePython","Rebar")
            OsafeRebar(obj)
            obj.Label = translate("osafe","Rebar")
            obj.strip = strip
            obj.top_diameter = top_rebar_diameter
            obj.bot_diameter = bot_rebar_diameter
            obj.stirrup_diameter = stirrup_diameter
            obj.extended = extended
            obj.min_ratio_of_rebars = min_ratio_of_rebars
            foundation = doc.Foundation
            obj.foundation = foundation
            if FreeCAD.GuiUp:
                ViewProviderOsafeRebar(obj.ViewObject)
            rebars.addObject(obj)
    return rebars


class OsafeRebar(ArchComponent.Component):

    "A parametric reinforcement bar (rebar) object"

    def __init__(self,obj):

        ArchComponent.Component.__init__(self,obj)
        self.setProperties(obj)
        obj.IfcType = "Reinforcing Bar"

    def setProperties(self,obj):
        pl = obj.PropertiesList
        if "strip" not in pl:
            obj.addProperty(
                prop_link,
                "strip",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The Strip"))
        if "number_of_top_rebars" not in pl:
            obj.addProperty(
                prop_integer,
                "number_of_top_rebars",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The top amount of bars")
                ).number_of_top_rebars=0
        if "number_of_bot_rebars" not in pl:
            obj.addProperty(
                prop_integer,
                "number_of_bot_rebars",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The bottom amount of bars")
                ).number_of_bot_rebars=0
        if "spacing" not in pl:
            obj.addProperty(
                prop_length,
                "spacing",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The spacing between the bars")
                ).spacing=0
            obj.setEditorMode("spacing", 1)
        if "foundation" not in pl:
            obj.addProperty(
                prop_link,
                "foundation",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The Foundation"))
        if "top_diameter" not in pl:
            obj.addProperty(
                prop_length,
                "top_diameter",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The diameter of the top bar"))
        if "bot_diameter" not in pl:
            obj.addProperty(
                prop_length,
                "bot_diameter",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The diameter of the bottom bar"))
        if "stirrup_diameter" not in pl:
            obj.addProperty(
                prop_length,
                "stirrup_diameter",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The diameter of the stirrup bar"))
        if "factor_after_arc" not in pl:
            obj.addProperty(
                prop_float,
                "factor_after_arc",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "This value is multiplied by the bar diameter.")
                ).factor_after_arc=16
        if "width" not in pl:
            obj.addProperty(
                prop_length,
                "width",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The total width to span the rebars over. Keep 0 to automatically use the strip width.")
                ).width=0
        if "height" not in pl:
            obj.addProperty(
                prop_length,
                "height",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The height of strip. Keep 0 to automatically use the foundation height.")
                ).height=0
        if "cover" not in pl:
            obj.addProperty(
                prop_length,
                "cover",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The cover of strip. Keep 0 to automatically use the foundation cover.")
                ).cover=0
        if "rounding" not in pl:
            obj.addProperty(
                prop_float,
                "rounding",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "The fillet to apply to the angle of the base profile. This value is multiplied by the bar diameter.")
                ).rounding=3
        if "min_ratio_of_rebars" not in pl:
            obj.addProperty(
                prop_float,
                "min_ratio_of_rebars",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "Minimum rebar ratio")
                )
        if "extended" not in pl:
            obj.addProperty(
                prop_dist,
                "extended",
                "Rebar",
                QT_TRANSLATE_NOOP(app_prop,
                "Extended length of base rebar")
                ).extended=0
        if "top_length" not in pl:
            obj.addProperty(
                prop_dist,
                "top_length",
                "Bill",
                QT_TRANSLATE_NOOP(app_prop,
                "Total length of all top rebars"))
            obj.setEditorMode("top_length", 1)
        if "bot_length" not in pl:
            obj.addProperty(
                prop_dist,
                "bot_length",
                "Bill",
                QT_TRANSLATE_NOOP(app_prop,
                "Total length of all bot rebars"))
            obj.setEditorMode("bot_length", 1)
        if not hasattr(obj, "top_weight"):
            obj.addProperty(
                prop_float,
                "top_weight",
                "Bill",
                "The weight of top rebars (ton)",
                )
        if not hasattr(obj, "bot_weight"):
            obj.addProperty(
                prop_float,
                "bot_weight",
                "Bill",
                "The weight of bottom rebars (ton)",
                )
        if not hasattr(obj, "total_weight"):
            obj.addProperty(
                prop_float,
                "total_weight",
                "Bill",
                "The weight of top and bottom rebars (ton)",
                )
        # if "placement_list" not in pl:
        #     obj.addProperty(
        #         "App::PropertyPlacementList",
        #         "placement_list",
        #         "Rebar",
        # QT_TRANSLATE_NOOP(app_prop,
        #         "List of placement of all the bars"))
        # if "length" not in pl:
        #     obj.addProperty(
        #         prop_dist,
        #         "length",
        #         "Rebar",
        #         QT_TRANSLATE_NOOP(app_prop,
        #         "Length of a single rebar"))
        #     obj.setEditorMode("length", 1)
        # if "mark" not in pl:
        #     obj.addProperty(
        #         prop_string,
        #         "mark",
        #         "Rebar",
        #         QT_TRANSLATE_NOOP(app_prop,
        #         "The rebar mark"),
        #     )
        self.Type = "Rebar"

    def onDocumentRestored(self,obj):
        ArchComponent.Component.onDocumentRestored(self,obj)
        self.setProperties(obj)

    # def onChanged(self, obj, prop):
    #     if prop == "strip" and hasattr(obj,"strip") and obj.strip:
    #         # mark strip to recompute so it can detect this object
    #         obj.strip.touch()

    def execute(self,obj):
        top_rebar_shapes, bot_rebar_shapes, top_wires, bot_wires = osf.get_top_bot_rebar_shapes_from_strip_and_foundation(
        obj.strip,
        obj.top_diameter.Value,
        obj.bot_diameter.Value,
        obj.number_of_top_rebars,
        obj.number_of_bot_rebars,
        obj.width.Value,
        obj.height.Value,
        obj.cover.Value,
        obj.stirrup_diameter.Value,
        obj.foundation,
        None,
        obj.rounding,
        obj.factor_after_arc,
        obj.extended.Value,
        obj.min_ratio_of_rebars,
        )
        self.top_wires = top_wires
        self.bot_wires = bot_wires
        obj.top_length = osf.get_total_length_of_shapes(top_wires)
        obj.bot_length = osf.get_total_length_of_shapes(bot_wires)
        obj.top_weight = osf.get_total_volume_of_shapes(top_rebar_shapes) * 7850e-12
        obj.bot_weight = osf.get_total_volume_of_shapes(bot_rebar_shapes) * 7850e-12
        obj.total_weight = obj.top_weight + obj.bot_weight
        obj.Shape = Part.makeCompound(top_rebar_shapes + bot_rebar_shapes)

class ViewProviderOsafeRebar(ArchComponent.ViewProviderComponent):

    "A View Provider for the Rebar object"

    def __init__(self,vobj):

        ArchComponent.ViewProviderComponent.__init__(self,vobj)
        self.setProperties(vobj)
        vobj.ShapeColor = ArchCommands.getDefaultColor("Rebar")

    def setProperties(self,vobj):

        pl = vobj.PropertiesList
        if not "RebarShape" in pl:
            vobj.addProperty(
                prop_string,"RebarShape","Rebar",
                QT_TRANSLATE_NOOP(app_prop,"Shape of rebar")).RebarShape
            vobj.setEditorMode("RebarShape",2)

    def onDocumentRestored(self,vobj):

        self.setProperties(vobj)

    def getIcon(self):
        return str(Path(__file__).parent.parent / "osafe_images" / "osafe_rebar.svg")
    
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

    def updateData(self,obj,prop):

        if prop == "Shape":
            if hasattr(self,"centerline") and self.centerline:
                self.centerlinegroup.removeChild(self.centerline)
            if hasattr(obj.Proxy,"top_wires") and obj.Proxy.top_wires:
                from pivy import coin
                import re
                self.centerline = coin.SoSeparator()
                wires = obj.Proxy.top_wires + obj.Proxy.bot_wires
                comp = Part.makeCompound(wires)
                pts = re.findall("point \[(.*?)\]",comp.writeInventor().replace("\n",""))
                pts = [p.split(",") for p in pts]
                for pt in pts:
                    ps = coin.SoSeparator()
                    plist = []
                    for p in pt:
                        c = []
                        for pstr in p.split(" "):
                            if pstr:
                                c.append(float(pstr))
                        plist.append(c)
                    coords = coin.SoCoordinate3()
                    coords.point.setValues(plist)
                    ps.addChild(coords)
                    ls = coin.SoLineSet()
                    ls.numVertices = -1
                    ps.addChild(ls)
                    self.centerline.addChild(ps)
                self.centerlinegroup.addChild(self.centerline)
        ArchComponent.ViewProviderComponent.updateData(self,obj,prop)

    def attach(self,vobj):

        from pivy import coin
        self.centerlinegroup = coin.SoSeparator()
        self.centerlinegroup.setName("Centerline")
        self.centerlinecolor = coin.SoBaseColor()
        self.centerlinestyle = coin.SoDrawStyle()
        self.centerlinegroup.addChild(self.centerlinecolor)
        self.centerlinegroup.addChild(self.centerlinestyle)
        vobj.addDisplayMode(self.centerlinegroup,"Centerline")
        ArchComponent.ViewProviderComponent.attach(self,vobj)

    def onChanged(self,vobj,prop):

        if (prop == "LineColor") and hasattr(vobj,"LineColor"):
            if hasattr(self,"centerlinecolor"):
                c = vobj.LineColor
                self.centerlinecolor.rgb.setValue(c[0],c[1],c[2])
        elif (prop == "LineWidth") and hasattr(vobj,"LineWidth"):
            if hasattr(self,"centerlinestyle"):
                self.centerlinestyle.lineWidth = vobj.LineWidth
        ArchComponent.ViewProviderComponent.onChanged(self,vobj,prop)

    def getDisplayModes(self,vobj):

        modes=["Centerline"]
        return modes+ArchComponent.ViewProviderComponent.getDisplayModes(self,vobj)


class Ui:
    def __init__(self, rebar_obj=None):
        import os
        self.form = Gui.PySideUic.loadUi(str(Path(__file__).parent.parent / "osafe_widgets" / "edit_objects" / "edit_osafe_rebars.ui"))
        self.rebar_obj = rebar_obj
        self.create_connections()
        self.original_values = self.fill_form()

    def create_connections(self):
        self.form.top_rebar_diameter_combobox.currentIndexChanged.connect(self.modify_rebar)
        self.form.bot_rebar_diameter_combobox.currentIndexChanged.connect(self.modify_rebar)
        self.form.stirrup_rebar_diameter_combobox.currentIndexChanged.connect(self.modify_rebar)
        self.form.extended_spinbox.valueChanged.connect(self.modify_rebar)
        self.form.cover_spinbox.valueChanged.connect(self.modify_rebar)
        self.form.height_spinbox.valueChanged.connect(self.modify_rebar)
        self.form.width_spinbox.valueChanged.connect(self.modify_rebar)
        self.form.impose_minimum_spinbox.valueChanged.connect(self.modify_rebar)
        self.form.accept_pushbutton.clicked.connect(self.accept)
        self.form.cancel_pushbutton.clicked.connect(self.reject)

    def fill_form(self):
        top_diameter = self.rebar_obj.top_diameter
        top_index = self.form.top_rebar_diameter_combobox.findText(str(int(top_diameter)))
        self.form.top_rebar_diameter_combobox.setCurrentIndex(top_index)
        bot_diameter = self.rebar_obj.bot_diameter 
        bot_index = self.form.bot_rebar_diameter_combobox.findText(str(int(bot_diameter)))
        self.form.bot_rebar_diameter_combobox.setCurrentIndex(bot_index)
        stirrup_diameter = self.rebar_obj.stirrup_diameter
        stirrup_index = self.form.stirrup_rebar_diameter_combobox.findText(str(int(stirrup_diameter)))
        self.form.stirrup_rebar_diameter_combobox.setCurrentIndex(stirrup_index) 
        extended = self.rebar_obj.extended.Value
        self.form.extended_spinbox.setValue(extended / 10)
        cover = self.rebar_obj.cover.Value
        self.form.cover_spinbox.setValue(cover / 10)
        height = self.rebar_obj.height.Value
        self.form.height_spinbox.setValue(height / 10)
        width = self.rebar_obj.width.Value
        self.form.width_spinbox.setValue(width / 10)
        min_ratio = self.rebar_obj.min_ratio_of_rebars
        self.form.impose_minimum_spinbox.setValue(min_ratio)
        self.set_properties()
        return {
        "top_diameter": top_diameter,
        "bot_diameter": bot_diameter,
        "stirrup_diameter": stirrup_diameter,
        "extended": extended,
        "cover": cover,
        "height": height,
        "width": width,
        "min_ratio": min_ratio,
        }

    def accept(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def reject(self):
        self.rebar_obj.top_diameter = self.original_values["top_diameter"]
        self.rebar_obj.bot_diameter = self.original_values["bot_diameter"]
        self.rebar_obj.stirrup_diameter = self.original_values["stirrup_diameter"]
        self.rebar_obj.extended = self.original_values["extended"]
        self.rebar_obj.cover = self.original_values["cover"]
        self.rebar_obj.height = self.original_values["height"]
        self.rebar_obj.width = self.original_values["width"]
        self.rebar_obj.min_ratio_of_rebars = self.original_values["min_ratio"]
        self.rebar_obj.recompute(True)
        Gui.Control.closeDialog()

    def modify_rebar(self):
        self.rebar_obj.top_diameter = int(self.form.top_rebar_diameter_combobox.currentText())
        self.rebar_obj.bot_diameter = int(self.form.bot_rebar_diameter_combobox.currentText())
        self.rebar_obj.stirrup_diameter = int(self.form.stirrup_rebar_diameter_combobox.currentText())
        self.rebar_obj.extended = self.form.extended_spinbox.value() * 10
        self.rebar_obj.cover = self.form.cover_spinbox.value() * 10
        self.rebar_obj.height = self.form.height_spinbox.value() * 10
        self.rebar_obj.width = self.form.width_spinbox.value() * 10
        self.rebar_obj.min_ratio_of_rebars = self.form.impose_minimum_spinbox.value()
        self.rebar_obj.recompute(True)
        self.set_properties()

    def set_properties(self):
        self.form.total_top_length_spinbox.setValue(self.rebar_obj.top_length.Value / 1000)
        self.form.total_bot_length_spinbox.setValue(self.rebar_obj.bot_length.Value / 1000)
        self.form.total_top_weight_spinbox.setValue(self.rebar_obj.top_weight * 1000)
        self.form.total_bot_weight_spinbox.setValue(self.rebar_obj.bot_weight * 1000)
        self.form.total_weight_spinbox.setValue(self.rebar_obj.total_weight * 1000)