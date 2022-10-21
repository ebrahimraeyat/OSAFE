from math import sqrt
import Draft
import Arch
import Part
import FreeCAD as App
import FreeCADGui as Gui
import pandas as pd
try:
    from safe.punch import safe
    from safe.punch.axis import create_grids
    from safe.punch import foundation
    from safe.punch.punch import make_punch
except:
    import safe
    from axis import create_grids
    import foundation
    from punch import make_punch


class Geom(object):

    def __init__(self, filename=None):
        # self.bar_label = form.bar_label
        if filename:
            self._safe = safe.Safe(filename)
            self.solid_slabs = self._safe.solid_slabs
            self.slab_prop_assignment = self._safe.slab_prop_assignment
            self.load_combinations = self._safe.load_combinations
            self.point_loads = self._safe.points_loads

    def create_vectors(self, points_prop=None):
        vectors = {}
        # self.bar_label.setText("Reading Points Geometry")
        for key, value in points_prop.items():
            vectors[key] = App.Vector(round(value.x, 4), round(value.y, 4), int(value.z))
        return vectors

    def create_areas(self, areas_prop):
        areas = {}
        # self.bar_label.setText("Creating Areas Geometry")
        for key, points_id in areas_prop.items():
            points = [self.obj_geom_points[point_id] for point_id in points_id]
            points.append(points[0])
            areas[key] = Part.Face(Part.makePolygon(points))
        return areas

    def create_structures(self, areas):
        # self.bar_label.setText("Creating structures Geometry")
        areas_thickness = self._safe.get_thickness(areas)
        structures = {}
        for key, area in areas.items():
            thickness = areas_thickness[key] - 93
            structures[key] = area.extrude(App.Vector(0, 0, -thickness))
        return structures

    def create_fusion(self, structures):
        # self.bar_label.setText("Creating One Slab Geometry")
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
        else:
            s1 = slab_struc[0]
            fusion = s1.fuse(slab_struc[1:])
        if bool(slab_opening):
            print('openings')
            fusion = fusion.cut(slab_opening)
            
        return fusion

    def create_foundation(self, fusion):
        # self.bar_label.setText("Creating Foundation Geometry")
        if hasattr(fusion, "removeSplitter"):
            return fusion.removeSplitter()
        return fusion

    def create_punches(self):
        # self.bar_label.setText("Creating Punch Objects")
        for f in self.foundation.Faces:
            if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
                foundation_plan = f
                break
        d = self.foundation.BoundBox.ZLength
        cover = 93
        h = d + cover
        fc = self._safe.fc
        foun_obj = foundation.make_foundation(foundation_plan, height=h, cover=cover, fc=fc)
        for key in self.columns_id:
            value = self._safe.point_loads[key]
            bx = value['xdim']
            by = value['ydim']
            combos_load = self._safe.points_loads_combinations[self._safe.points_loads_combinations['Point'] == key]
            d = {}
            for row in combos_load.itertuples():
                combo = row.Combo
                F = row.Fgrav
                Mx = row.Mx
                My = row.My
                d[combo] = f"{F}, {Mx}, {My}"
            point = self._safe.obj_geom_points[key]
            center_of_load = App.Vector(point.x, point.y, 0)
            column = make_column(bx, by, center_of_load, d)
            p = make_punch(
                foun_obj,
                column,
                )
            # App.ActiveDocument.recompute()
            l = p.Location
            pl = App.Vector(0, 0, 4100)
            t = '0.0'
            text = Draft.make_text([t, l], placement=pl)
            p.Ratio = t
            text.ViewObject.FontSize = 200
            p.text = text
            p.id = str(key)

    def grid_lines(self):
        if not App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("draw_grid", True):
            return

        gridLines = self._safe.grid_lines()
        if gridLines is None:
            return
        x_grids = gridLines['x']
        y_grids = gridLines['y']
        b = self.foundation.BoundBox
        create_grids(x_grids, b, 'x')
        create_grids(y_grids, b, 'y')

    def plot(self):
        self.obj_geom_points = self.create_vectors(self._safe.obj_geom_points)
        obj_geom_areas = self.create_areas(self._safe.obj_geom_areas)
        self.columns_id = list(self._safe.point_loads.keys())
        structures = self.create_structures(obj_geom_areas)
        del obj_geom_areas
        fusion = self.create_fusion(structures)
        Gui.SendMsgToActiveView("ViewFit")
        self.foundation = self.create_foundation(fusion)
        self.grid_lines()
        self.create_punches()
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewAxonometric()
        # self.bar_label.setText("")

def make_column(
    bx : float,
    by : float,
    center : App.Vector,
    combos_load : dict,
    ):
    dz = 4000
    v2 = App.Vector(center.x, center.y, dz)
    line = Draft.make_line(center, v2)
    line.recompute()
    section_name = f'BOX{bx}X{by}'
    # profile = get_profile(section_name, None)
    # if profile is None:
    profile = Arch.makeProfile(
        profile=[
                0,
                'REC',
                section_name,
                'R',
                bx, # T3
                by, # height
                ])
    col = Arch.makeStructure(profile)
    col.Nodes = [center, v2]
    place_the_beam(col, line)
    rotation = 0
    col.AttachmentOffset = App.Placement(
            App.Vector(0, 0, 0),
            App.Rotation(App.Vector(0,0,1),rotation))
    if not hasattr(col, "combos_load"):
        col.addProperty(
            "App::PropertyMap",
            "combos_load",
            "Structure",
            ).combos_load = combos_load
    col.setEditorMode('combos_load', 2)
    col.IfcType = 'Column'
    col.PredefinedType = 'COLUMN'
    col.recompute()
    if App.GuiUp:
        col.ViewObject.LineWidth = 1.00
        col.ViewObject.PointSize = 1.00
        col.ViewObject.Transparency = 30
    return col

def place_the_beam(beam, line):
    '''arg1= beam, arg2= edge: lay down the selected beam on the selected edge'''
    edge = line.Shape.Edges[0]
    vect=edge.tangentAt(0)
    beam.Placement.Rotation=App.Rotation(0,0,0,1)
    rot=App.Rotation(beam.Placement.Rotation.Axis,vect)
    beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
    beam.Placement.Base=edge.valueAt(0)
    beam.addExtension("Part::AttachExtensionPython")
    beam.Support=[(line, 'Edge1')]
    beam.MapMode='NormalToEdge'
    beam.MapReversed=True
    beam.Height=edge.Length

def open(filename):
    import os
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = App.newDocument(docname)
    doc.Label = docname
    doc = insert(filename, doc.Name)
    return doc


def insert(filename, docname):
    geom = Geom(filename)
    geom.plot()