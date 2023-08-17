from math import sqrt
import Draft
import Arch
import Part
import FreeCAD as App
import FreeCADGui as Gui
import pandas as pd


class Geom(object):

    def __init__(self, filename=None):
        if filename:
            self._safe = safe.Safe(filename)
            self.solid_slabs = self._safe.solid_slabs
            self.slab_prop_assignment = self._safe.slab_prop_assignment
            self.point_loads = self._safe.points_loads
            self.removeSplitter = True

    def create_vectors(self, points_prop=None):
        vectors = {}
        for key, value in points_prop.items():
            vectors[key] = App.Vector(round(value.x, 4), round(value.y, 4), int(value.z))
        return vectors

    def create_areas(self, areas_prop):
        areas = {}
        for key, points_id in areas_prop.items():
            points = [self.obj_geom_points[point_id] for point_id in points_id]
            areas[key] = Draft.makeWire(points, closed=True, face=True, support=None)
        return areas

    def create_column(self, point_loads_prop):
        areas = {}
        for key, value in point_loads_prop.items():
            pl = App.Placement()
            length = value['xdim']
            height = value['ydim']
            if not (length and height):
                continue
            v = self.obj_geom_points[key]
            v.x = v.x - length / 2
            v.y = v.y - height / 2
            pl.Base = v
            areas[key] = Draft.makeRectangle(length=length, height=height, placement=pl, face=True, support=None)
        return areas

    def create_structures(self, areas):
        areas_thickness = self._safe.get_thickness(areas)
        structures = {}
        for key, area in areas.items():
            thickness = areas_thickness[key] - 93
            structures[key] = Arch.makeStructure(area, height=thickness)
            Draft.autogroup(structures[key])
            Draft.move(structures[key], App.Vector(0, 0, -thickness), copy=False)
        return structures

    def create_fusion(self, structures, doc):
        slab_struc = []
        slab_opening = []
        for key, value in structures.items():
            if self.slab_prop_assignment[key] == 'None':
                slab_opening.append(value)
            else:
                slab_struc.append(value)
        if len(slab_struc) == 1:
            print('one slab')
            fusion = slab_struc[0]
            self.removeSplitter = False
        else:
            fusion = doc.addObject("Part::MultiFuse", "Fusion")
            doc.Fusion.Shapes = slab_struc
        if bool(slab_opening):
            print('openings')
            base = fusion
            for opening in slab_opening:
                cut = doc.addObject("Part::Cut", "Cut")
                cut.Base = base
                cut.Tool = opening
                base = cut
            return cut
        return fusion

    def create_foundation(self, fusion, doc, gui):
        if not self.removeSplitter:
            foun = doc.addObject('Part::Feature', 'Foun')
            foun.Shape = fusion.Shape
            return foun
        foun = doc.addObject('Part::Feature', 'Foun')
        foun.Shape = fusion.Shape.removeSplitter()
        doc.removeObject(fusion.Label)
        # gui.getObject(fusion.Name).Visibility = False
        return foun

    # def create_3D_column(self, columns):
    #     for key, area in columns.items():
    #         col = Part.makeBox(area.Length, area.Height, 4000, area.Placement.Base)
    #         self.punchs[key].Shape = col
        # self.punchs[key].number = int(key)

    # def point_loads_is_in_witch_areas(self, areas, points_loads, obj_geom_points):
    #   ''' search areas that special point is in it/them
    #    it return a dictionary with keys = special points ids
    #    and a list of areas that special point is in as value
    #    '''
    #   point_loads_areas_contain = {}
    #   for _id in points_loads.keys():
    #       coord = obj_geom_points[_id]
    #       p = App.Vector(coord.x, coord.y, coord.z)
    #       curr_areas = {}
    #       for key, value in areas.items():
    #           if value.Shape.isInside(p, .01, True):
    #               curr_areas[key] = value
    #       point_loads_areas_contain[_id] = curr_areas
    #   return point_loads_areas_contain

    def grid_lines(self):
        if not App.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetBool("draw_grid", True):
            return

        gridLines = self._safe.grid_lines()
        if gridLines is None:
            return
        x_grids = gridLines['x']
        y_grids = gridLines['y']
        b = self.foundation.Shape.BoundBox
        x_axis_length = b.YLength * 1.2
        y_axis_length = b.XLength * 1.2
        x_grids_coord = -b.YLength * .1
        y_grids_coord = b.XLength * 1

        for text, coord in x_grids.items():
            ax = Arch.makeAxis(1)
            ax.Distances = [coord]
            ax.Length = x_axis_length
            ax.CustomNumber = str(text)
            ax.Placement.Base.y = b.YMin
            Draft.move(ax, App.Vector(0, x_grids_coord, 0), copy=False)
            ax_gui = ax.ViewObject
            ax_gui.BubbleSize = 1500
            ax_gui.FontSize = 750
        for text, coord in y_grids.items():
            ax = Arch.makeAxis(1)
            ax.Length = y_axis_length
            ax.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), 90))
            ax.Distances = [coord]
            ax.CustomNumber = str(text)
            Draft.move(ax, App.Vector(y_grids_coord, 0, 0), copy=False)
            ax_gui = ax.ViewObject
            ax_gui.BubbleSize = 1500
            ax_gui.FontSize = 750

    def plot(self):
        doc = App.ActiveDocument
        gui = Gui.ActiveDocument
        self.obj_geom_points = self.create_vectors(self._safe.obj_geom_points)
        obj_geom_areas = self.create_areas(self._safe.obj_geom_areas)
        self.obj_geom_point_loads = self.create_column(self._safe.point_loads)
        self.columns_number = list(self._safe.point_loads.keys())
        self.structures = self.create_structures(obj_geom_areas)
        del obj_geom_areas
        self.fusion = self.create_fusion(self.structures, doc)
        doc.recompute()
        self.foundation = self.create_foundation(self.fusion, doc, gui)
        self.grid_lines()
        doc.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        # Gui.activeDocument().activeView().viewAxonometric()
        # Gui.activeDocument().activeView().setCameraType("Perspective")

    @staticmethod
    def __get_color(pref_intity, color=674321151):
        c = App.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetUnsigned(pref_intity, color)
        r = float((c >> 24) & 0xFF) / 255.0
        g = float((c >> 16) & 0xFF) / 255.0
        b = float((c >> 8) & 0xFF) / 255.0
        return (r, g, b)
