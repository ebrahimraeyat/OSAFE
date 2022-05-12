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


FreeCADGui.addCommand('osafe_wireframe_views',WireFrameView())