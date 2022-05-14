#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2018 Yorik van Havre <yorik@uncreated.net>              *
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

"""This module contains FreeCAD commands for the OSAFE workbench"""


from pathlib import Path

import FreeCAD, Draft
import FreeCADGui

def QT_TRANSLATE_NOOP(ctx, txt): return txt

class WireFrameView:

    def GetResources(self):
        return {'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "wireframe.svg"),
                'MenuText': QT_TRANSLATE_NOOP("CivilTools_Views", "WireFrame"),
                'ToolTip' : QT_TRANSLATE_NOOP("CivilTools_Views", "Show Wire Frame Model"),
                # 'Accel': 'Ctrl+9',
                'Checkable': False,
                }

    def Activated(self, index):
        show_column = True
        show_beam = True
        show_arch_wall = True
        show_face = True
        if index == 0:
            wireframe = False
        else:
            wireframe = True

        for obj in FreeCAD.ActiveDocument.Objects:
            if Draft.getType(obj) == "Sketcher::SketchObject":
                continue
            if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, 'Type') and obj.Proxy.Type == 'Profile':
                continue
            show_obj = False

            if hasattr(obj, 'IfcType'):
                if obj.IfcType == 'Beam':
                    show_obj = show_beam and not wireframe
                elif obj.IfcType == 'Column':
                    show_obj = show_column and not wireframe
                elif obj.IfcType in ('Wall', 'Window'):
                    show_obj = show_arch_wall
                elif obj.IfcType == 'Footing':
                    show_obj = not wireframe
            # elif obj.Label.startswith('W') and hasattr(obj,'MakeFace'):
            #     show_obj = show_face
            elif obj.Label.endswith('CenterLine'):
                if obj.Label.startswith('B'):
                    show_obj = show_beam and wireframe
                elif obj.Label.startswith('C'):
                    show_obj = show_column and wireframe
            elif hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
                if obj.Proxy.Type == 'BaseFoundation':
                    # if len(obj.Base.InList) > 1:
                    #     show_obj = False
                    # else:
                    show_obj = not wireframe
                elif obj.Proxy.Type == 'Beam':
                    show_obj = True
                elif obj.Proxy.Type == 'Wire':
                    if hasattr(obj, 'MakeFace') and obj.MakeFace == True:
                        show_obj = True
                    else:
                        show_obj = wireframe
            show_object(obj, show_obj)
        FreeCAD.ActiveDocument.recompute()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
                

def show_object(obj, show : bool):
    if show:
        obj.ViewObject.show()
    else:
        obj.ViewObject.hide()



class OSAFEViewBaseFoundation:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == 'BaseFoundation':
                show_object(obj, index)
                for c in obj.ViewObject.claimChildren():
                    show_object(c, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_base_foundation.svg"),
            'MenuText': 'Base Foundations', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewArchWall:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Wall':
                show_object(obj, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_arch_wall.svg"),
            'MenuText': 'Arch Wall', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewColumns:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                show_object(obj, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_columns.svg"),
            'MenuText': 'Columns', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewBeams:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == 'Beam':
                show_object(obj, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_beams.svg"),
            'MenuText': 'Beams', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewSlabs:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type in ('Slab', 'RectangularSlab'):
                show_object(obj, index)
                for c in obj.ViewObject.claimChildren():
                    show_object(c, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_slabs.svg"),
            'MenuText': 'Slabs', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewFoundations:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == 'Foundation':
                show_object(obj, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_foundations.svg"),
            'MenuText': 'Foundations', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewDesignLayerA:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == 'Strip' and obj.layer == 'A':
                show_object(obj, index)
                for c in obj.ViewObject.claimChildren():
                    show_object(c, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_design_layer_a.svg"),
            'MenuText': 'Layer A', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewDesignLayerB:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == 'Strip' and obj.layer == 'B':
                show_object(obj, index)
                for c in obj.ViewObject.claimChildren():
                    show_object(c, index)

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_design_layer_b.svg"),
            'MenuText': 'Layer B', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class OSAFEViewPunch:
    def Activated(self, index):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == 'Punch':
                show_object(obj, index)
                for c in obj.ViewObject.claimChildren():
                    show_object(c, index)
                    

    def GetResources(self):
        return { 
            'Pixmap'  : str(Path(__file__).parent / "Resources" / "icons" / "view_punch.svg"),
            'MenuText': 'Punch', 
            'Checkable': True,
            }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None



class OSAFEViewGroupCommand:
    def GetCommands(self):
        return (
            "osafe_wireframe_views",
            "OSAFE_view_basefoundation",
            "OSAFE_view_columns",
            "OSAFE_view_beams",
            "OSAFE_view_slabs",
            "OSAFE_view_foundations",
            "OSAFE_view_design_layer_a",
            "OSAFE_view_design_layer_b",
            "OSAFE_view_punch",
            "OSAFE_view_arch_wall",

            ) # a tuple of command names that you want to group

    # def Activated(self, index):
    #     if index == 0:
    #         FSMatchOuter = False
    #         FreeCAD.Console.PrintLog("Set auto diameter to match inner thread\n")
    #     else:
    #         FSMatchOuter = True
    #         FreeCAD.Console.PrintLog("Set auto diameter to match outer thread\n")

    def GetDefaultCommand(self): # return the index of the tuple of the default command. This method is optional and when not implemented '0' is used 
        return 1

    def GetResources(self):
        return { 'MenuText': 'Screw diamter matching mode', 'ToolTip': 'Screw diamter matching mode (by inner or outer thread diameter)', 'DropDownMenu': False, 'Exclusive' : False }
       
    def IsActive(self): # optional
        return True

FreeCADGui.addCommand('osafe_wireframe_views',WireFrameView())
FreeCADGui.addCommand('OSAFE_view_basefoundation',OSAFEViewBaseFoundation())
FreeCADGui.addCommand('OSAFE_view_columns',OSAFEViewColumns())
FreeCADGui.addCommand('OSAFE_view_beams',OSAFEViewBeams())
FreeCADGui.addCommand('OSAFE_view_slabs',OSAFEViewSlabs())
FreeCADGui.addCommand('OSAFE_view_foundations',OSAFEViewFoundations())
FreeCADGui.addCommand('OSAFE_view_design_layer_a',OSAFEViewDesignLayerA())
FreeCADGui.addCommand('OSAFE_view_design_layer_b',OSAFEViewDesignLayerB())
FreeCADGui.addCommand('OSAFE_view_punch',OSAFEViewPunch())
FreeCADGui.addCommand('OSAFE_view_arch_wall',OSAFEViewArchWall())
FreeCADGui.addCommand('OSAFE_view_group',OSAFEViewGroupCommand())
