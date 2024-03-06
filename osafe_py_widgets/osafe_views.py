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

import FreeCAD
import FreeCADGui


def QT_TRANSLATE_NOOP(ctx, txt):
    return txt

def show_object(obj, index: int):
    if index == 0:
        obj.ViewObject.hide()
    else:
        obj.ViewObject.show()


class WireFrameView:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "wireframe.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("CivilTools_Views", "WireFrame"),
            "ToolTip": QT_TRANSLATE_NOOP("CivilTools_Views", "Show Wire Frame Model"),
            # 'Accel': 'Ctrl+9',
            "Checkable": True,
        }

    def Activated(self, index):
        pass

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class OSAFEViewBaseFoundation:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_base_foundation.svg"
                ),
            "MenuText": "Base Foundations",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
                if obj.Proxy.Type == "BaseFoundation":
                    show_object(obj, index)
                    show_object(obj.Base, index)
                elif obj.Proxy.Type in ("Strip", "Rebar") and index != 0:
                    obj.ViewObject.hide()
                    if hasattr(obj, "Base") and hasattr(obj.Base, "ViewObject"):
                        obj.Base.ViewObject.hide()

class OSAFEViewRebars:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_osafe_rebar.svg"
                ),
            "MenuText": "Rebars",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
                if obj.Proxy.Type == "Rebar":
                    show_object(obj, index)
                elif obj.Proxy.Type in ("Strip", "BaseFoundation") and index != 0:
                    obj.ViewObject.hide()
                    obj.Base.ViewObject.hide()


class OSAFEViewArchWall:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_arch_wall.svg"
            ),
            "MenuText": "Arch Wall",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "IfcType") and obj.IfcType in ("Wall", "Window"):
                show_object(obj, index)

                    
class OSAFEViewColumns:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_columns.svg"
            ),
            "MenuText": "Columns",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if (
                obj.Label.endswith("CenterLine") and obj.Label.startswith("C")
                ) or (
                hasattr(obj, "IfcType") and obj.IfcType == "Column"
                ):
                show_object(obj, index)


class OSAFEViewBeams:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_beams.svg"
            ),
            "MenuText": "Beams",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if (
                obj.Label.endswith("CenterLine") and obj.Label.startswith("B")
                ) or (
                hasattr(obj, "IfcType") and obj.IfcType == "Beam"
                ) or (
                    hasattr(obj, 'type') and
                    obj.type == "Beam"
                ):
                show_object(obj, index)


class OSAFEViewSlabs:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_slabs.svg"
            ),
            "MenuText": "Slabs",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type in  ('Slab', 'RectangularSlab'):
                show_object(obj, index)


class OSAFEViewFoundations:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_foundations.svg"
            ),
            "MenuText": "Foundations",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == "Foundation":
                show_object(obj, index)


class OSAFEViewDesignLayer:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_design_layer.svg"
            ),
            "MenuText": "Design Strip",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
                if obj.Proxy.Type == 'Strip':
                    show_object(obj, index)
                    show_object(obj.Base, index)
                elif obj.Proxy.Type in ("Rebar", "BaseFoundation") and index != 0:
                    obj.ViewObject.hide()
                    if hasattr(obj, "Base") and hasattr(obj.Base, "ViewObject"):
                            obj.Base.ViewObject.hide()


class OSAFEViewPunch:
    def GetResources(self):
        return {
            "Pixmap": str(
                Path(__file__).parent.parent / "osafe_images" / "view_punch.svg"
            ),
            "MenuText": "Punch",
            "Checkable": True,
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == "Punch":
                show_object(obj, index)
                for c in obj.ViewObject.claimChildren():
                    show_object(c, index)


FreeCADGui.addCommand("OSAFE_wireframe_views", WireFrameView())
FreeCADGui.addCommand("OSAFE_view_basefoundation", OSAFEViewBaseFoundation())
FreeCADGui.addCommand("OSAFE_view_columns", OSAFEViewColumns())
FreeCADGui.addCommand("OSAFE_view_beams", OSAFEViewBeams())
FreeCADGui.addCommand("OSAFE_view_slabs", OSAFEViewSlabs())
FreeCADGui.addCommand("OSAFE_view_foundations", OSAFEViewFoundations())
FreeCADGui.addCommand("OSAFE_view_design_layer", OSAFEViewDesignLayer())
FreeCADGui.addCommand("OSAFE_view_punch", OSAFEViewPunch())
FreeCADGui.addCommand("OSAFE_view_arch_wall", OSAFEViewArchWall())
FreeCADGui.addCommand("OSAFE_view_rebars", OSAFEViewRebars())
