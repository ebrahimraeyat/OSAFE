# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2018 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""This module contains FreeCAD commands for the OSAFE workbench"""


from pathlib import Path

import FreeCAD, Draft
import FreeCADGui


def QT_TRANSLATE_NOOP(ctx, txt):
    return txt

def show_object(obj, show: bool):
    if show:
        obj.ViewObject.show()
    else:
        obj.ViewObject.hide()


class WireFrameView:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "wireframe.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("CivilTools_Views", "WireFrame"),
            "ToolTip": QT_TRANSLATE_NOOP("CivilTools_Views", "Show Wire Frame Model"),
            # 'Accel': 'Ctrl+9',
            "Checkable": True,
        }

    def Activated(self, index):
        pass

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewBaseFoundation:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent
                / "Resources"
                / "icons"
                / "view_base_foundation.svg"
            ),
            "MenuText": "Base Foundations",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewArchWall:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "view_arch_wall.svg"
            ),
            "MenuText": "Arch Wall",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewColumns:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "view_columns.svg"
            ),
            "MenuText": "Columns",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewBeams:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "view_beams.svg"
            ),
            "MenuText": "Beams",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewSlabs:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "view_slabs.svg"
            ),
            "MenuText": "Slabs",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewFoundations:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "view_foundations.svg"
            ),
            "MenuText": "Foundations",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewDesignLayerA:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent
                / "Resources"
                / "icons"
                / "view_design_layer_a.svg"
            ),
            "MenuText": "Layer A",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewDesignLayerB:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent
                / "Resources"
                / "icons"
                / "view_design_layer_b.svg"
            ),
            "MenuText": "Layer B",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewPunch:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent / "Resources" / "icons" / "view_punch.svg"
            ),
            "MenuText": "Punch",
            "Checkable": True,
        }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewGroupCommand:
    def __init__(self):
        self.icon_status = {}
        for command in self.GetCommands():
            self.icon_status[command] = True

    def GetCommands(self):
        return (
            "OSAFE_wireframe_views",
            "OSAFE_view_basefoundation",
            "OSAFE_view_columns",
            "OSAFE_view_beams",
            "OSAFE_view_slabs",
            "OSAFE_view_foundations",
            "OSAFE_view_design_layer_a",
            "OSAFE_view_design_layer_b",
            "OSAFE_view_punch",
            "OSAFE_view_arch_wall",
        )  # a tuple of command names that you want to group

    def Activated(self, index):
        command = self.GetCommands()[index]
        self.icon_status[command] = not self.icon_status[command]
        wireframe = self.icon_status["OSAFE_wireframe_views"]
        show_base_foundation = self.icon_status["OSAFE_view_basefoundation"]
        show_column = self.icon_status["OSAFE_view_columns"]
        show_beam = self.icon_status["OSAFE_view_beams"]
        show_slab = self.icon_status["OSAFE_view_slabs"]
        show_foundation = self.icon_status["OSAFE_view_foundations"]
        show_design_layer_a = self.icon_status["OSAFE_view_design_layer_a"]
        show_design_layer_b = self.icon_status["OSAFE_view_design_layer_b"]
        show_punch = self.icon_status["OSAFE_view_punch"]
        show_arch_wall = self.icon_status["OSAFE_view_arch_wall"]
        # show_face = True
        reviwed_object = []

        for obj in FreeCAD.ActiveDocument.Objects:
            if obj.Name in reviwed_object:
                continue
            if Draft.getType(obj) == "Sketcher::SketchObject":
                continue
            if (
                hasattr(obj, "Proxy")
                and hasattr(obj.Proxy, "Type")
                and obj.Proxy.Type == "Profile"
            ):
                continue
            show_obj = False

            if hasattr(obj, "IfcType"):
                if obj.IfcType == "Beam":
                    show_obj = show_beam and not wireframe
                elif obj.IfcType == "Column":
                    show_obj = show_column and not wireframe
                elif obj.IfcType in ("Wall", "Window"):
                    show_obj = show_arch_wall
                elif obj.IfcType == "Footing":
                    if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, 'Type'):
                        if obj.Proxy.Type == "Foundation":
                            show_obj = show_foundation
                        elif obj.Proxy.Type == "BaseFoundation":
                            show_obj = show_base_foundation and not wireframe
                            base = obj.Base
                            show_object(base, (show_base_foundation and wireframe))
                            reviwed_object.append(base.Name)
                        elif obj.Proxy.Type in  ('Slab', 'RectangularSlab'):
                            show_obj = show_slab and not wireframe
                            base = obj.Base
                            show_object(base, (show_slab and wireframe))
                            reviwed_object.append(base.Name)
                            if hasattr(obj, 'plan'):
                                plan = obj.plan
                                show_object(plan, (show_slab and wireframe))
                                reviwed_object.append(plan.Name)
                elif (
                    hasattr(obj, 'Proxy') and 
                    hasattr(obj.Proxy, 'Type') and
                    obj.Proxy.Type == "Strip"
                    ):
                    if obj.layer == "A":
                        show_obj = show_design_layer_a and not wireframe
                        base = obj.Base
                        show_object(base, (show_design_layer_a and wireframe))
                        reviwed_object.append(base.Name)
                    elif obj.layer == "B":
                        show_obj = show_design_layer_b and not wireframe
                        base = obj.Base
                        show_object(base, (show_design_layer_b and wireframe))
                        reviwed_object.append(base.Name)
                    # else:
                    #     show_obj = show_slab and not wireframe
            elif obj.Label.endswith("CenterLine"):
                if obj.Label.startswith("B"):
                    show_obj = show_beam and wireframe
                elif obj.Label.startswith("C"):
                    show_obj = show_column and wireframe
            elif hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
                if obj.Proxy.Type == "Beam":
                    show_obj = show_beam
                # elif obj.Proxy.Type == "Wire":
                #     if hasattr(obj, "MakeFace") and obj.MakeFace == True:
                #         show_obj = show_slab
                    # else:
                    #     show_obj = show_slab and wireframe
                elif obj.Proxy.Type == "Punch":
                    show_obj = show_punch
                    for c in obj.ViewObject.claimChildren():
                        show_object(c, show_punch)
                        reviwed_object.append(c.Name)
                # elif obj.Proxy.Type == "Strip":
                #     if obj.layer == "A":
                #         show_obj = show_design_layer_a
                #     elif obj.layer == "B":
                #         show_obj = show_design_layer_b

            show_object(obj, show_obj)

    def GetDefaultCommand(self):
        return 0

    def GetResources(self):
        return {
            "MenuText": "Screw diamter matching mode",
            "ToolTip": "Screw diamter matching mode (by inner or outer thread diameter)",
            "DropDownMenu": False,
            "Exclusive": False,
        }

    # def IsActive(self): # optional
    #     return True


FreeCADGui.addCommand("OSAFE_wireframe_views", WireFrameView())
FreeCADGui.addCommand("OSAFE_view_basefoundation", OSAFEViewBaseFoundation())
FreeCADGui.addCommand("OSAFE_view_columns", OSAFEViewColumns())
FreeCADGui.addCommand("OSAFE_view_beams", OSAFEViewBeams())
FreeCADGui.addCommand("OSAFE_view_slabs", OSAFEViewSlabs())
FreeCADGui.addCommand("OSAFE_view_foundations", OSAFEViewFoundations())
FreeCADGui.addCommand("OSAFE_view_design_layer_a", OSAFEViewDesignLayerA())
FreeCADGui.addCommand("OSAFE_view_design_layer_b", OSAFEViewDesignLayerB())
FreeCADGui.addCommand("OSAFE_view_punch", OSAFEViewPunch())
FreeCADGui.addCommand("OSAFE_view_arch_wall", OSAFEViewArchWall())
FreeCADGui.addCommand("OSAFE_view_group", OSAFEViewGroupCommand())
