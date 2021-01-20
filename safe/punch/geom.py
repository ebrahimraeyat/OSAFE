from math import sqrt
import Draft
import Arch
import Part
import FreeCAD as App
import FreeCADGui as Gui
import pandas as pd
from safe.punch import safe
from safe.punch.punch_funcs import allowable_stress
from safe.punch.axis import create_grids
from safe.punch.punch_funcs import remove_obj
from safe.punch import foundation
from safe.punch.punch import make_punch


class Geom(object):

    def __init__(self, filename=None, form=None):
        self.progressbar = form.progressBar
        self.bar_label = form.bar_label
        if filename:
            self._safe = safe.Safe(filename)
            self.solid_slabs = self._safe.solid_slabs
            self.slab_prop_assignment = self._safe.slab_prop_assignment
            self.load_combinations = self._safe.load_combinations
            self.point_loads = self._safe.points_loads

    def create_vectors(self, points_prop=None):
        vectors = {}
        self.bar_label.setText("Reading Points Geometry")
        for key, value in points_prop.items():
            vectors[key] = App.Vector(round(value.x, 4), round(value.y, 4), int(value.z))
        return vectors

    def create_areas(self, areas_prop):
        areas = {}
        self.bar_label.setText("Creating Areas Geometry")
        for key, points_id in areas_prop.items():
            points = [self.obj_geom_points[point_id] for point_id in points_id]
            points.append(points[0])
            areas[key] = Part.Face(Part.makePolygon(points))
        return areas

    def create_structures(self, areas):
        self.bar_label.setText("Creating structures Geometry")
        areas_thickness = self._safe.get_thickness(areas)
        structures = {}
        for key, area in areas.items():
            thickness = areas_thickness[key] - 93
            structures[key] = area.extrude(App.Vector(0, 0, -thickness))
        return structures

    def create_fusion(self, structures):
        self.bar_label.setText("Creating One Slab Geometry")
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
        self.bar_label.setText("Creating Foundation Geometry")
        if hasattr(fusion, "removeSplitter"):
            return fusion.removeSplitter()
        return fusion

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

    def create_punches(self):
        self.bar_label.setText("Creating Punch Objects")
        for f in self.foundation.Faces:
            if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
                foundation_plane = f
                break
        d = self.foundation.BoundBox.ZLength
        cover = 93
        h = d + cover
        fc = self._safe.fc
        foun_obj = foundation.make_foundation(foundation_plane, height=h, cover=cover, fc=fc)
        punchs = {}

        for key in self.columns_number:
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
            p = make_punch(
                foundation_plane,
                foun_obj,
                bx,
                by,
                center_of_load,
                d,
                )
            App.ActiveDocument.recompute()
            length = bx * 1.5
            height = by * 1.5
            l = p.Location
            if l in ('Corner1', 'Corner4', 'Edge4', 'Interier'):
                length *= -1
            elif l in ('Edge1', 'Interier'):
                height *= -1
            # elif l in ('Edge3'):
            v = self.obj_geom_points[key]
            x = v.x + length
            y = v.y + height
            pl = App.Vector(x, y, 4100)
            t = '0.0'
            p.Ratio = t
            text = Draft.makeText([t, l], point=pl)
            text.ViewObject.FontSize = 200
            p.text = text
            # pl = App.Vector(v.x, v.y, 0)
            # p.Placement.Base = pl
            p.number = int(key)
            punchs[key] = p
        return punchs

    def grid_lines(self):
        if not App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("draw_grid", True):
            return

        gridLines = self._safe.grid_lines()
        if gridLines is None:
            return
        x_grids = gridLines['x']
        y_grids = gridLines['y']
        b = self.foundation.BoundBox
        # x_axis_length = b.YLength * 1.2
        # y_axis_length = b.XLength * 1.2
        # x_grids_coord = -b.YLength * .1
        # y_grids_coord = b.XLength * 1

        create_grids(x_grids, b, 'x')
        create_grids(y_grids, b, 'y')

        # for text, coord in x_grids.items():
        #     ax = Arch.makeAxis(1)
        #     ax.Distances = [coord]
        #     ax.Length = x_axis_length
        #     ax.CustomNumber = str(text)
        #     ax.Placement.Base.y = b.YMin
        #     Draft.move(ax, App.Vector(0, x_grids_coord, 0), copy=False)
        #     ax_gui = ax.ViewObject
        #     ax_gui.BubbleSize = 1500
        #     ax_gui.FontSize = 750
        # for text, coord in y_grids.items():
        #     ax = Arch.makeAxis(1)
        #     ax.Length = y_axis_length
        #     ax.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), 90))
        #     ax.Distances = [coord]
        #     ax.CustomNumber = str(text)
        #     Draft.move(ax, App.Vector(y_grids_coord, 0, 0), copy=False)
        #     ax_gui = ax.ViewObject
        #     ax_gui.BubbleSize = 1500
        #     ax_gui.FontSize = 750

    def plot(self):
        self.obj_geom_points = self.create_vectors(self._safe.obj_geom_points)
        obj_geom_areas = self.create_areas(self._safe.obj_geom_areas)
        self.columns_number = list(self._safe.point_loads.keys())
        structures = self.create_structures(obj_geom_areas)
        del obj_geom_areas
        fusion = self.create_fusion(structures)
        Gui.SendMsgToActiveView("ViewFit")
        self.foundation = self.create_foundation(fusion)
        self.grid_lines()
        self.punchs = self.create_punches()
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewAxonometric()
        self.bar_label.setText("")
        # self.progressbar.setValue(0)
        # Gui.activeDocument().activeView().setCameraType("Perspective")

    def ultimate_shear_stress(self):
        combos = self._safe.combos
        Vus_df = pd.DataFrame(index=combos)
        prop_df = pd.DataFrame(index=['I22', 'I33', 'I23', 'location', 'b0d', 'gammaـv2', 'gamma_v3', 'bx', 'by', 'x1', 'y1'])
        for punch in self.punchs.values():
            bx = punch.bx
            by = punch.by
            _id = punch.number
            location = punch.Location
            if not location:
                Vus_df[_id] = 0
                continue
            location = location.rstrip('1234').lower()
            gamma_fx = 1 / (1 + (2 / 3) * sqrt(by / bx))
            gamma_fy = 1 / (1 + (2 / 3) * sqrt(bx / by))
            gamma_vx = 1 - gamma_fx
            gamma_vy = 1 - gamma_fy
            I22 = punch.I22
            I33 = punch.I33
            I23 = punch.I23
            b0d = punch.Area
            x1, y1, _ = punch.center_of_load
            prop_df[_id] = [I22, I33, I23, punch.Location, b0d, gamma_vx, gamma_vy, bx, by, x1, y1]
            x3, y3, _ = punch.center_of_punch
            combos_load = punch.combos_load
            Vu_df = pd.DataFrame(index=combos)
            for col, f in enumerate(punch.faces.Faces):
                x4 = f.CenterOfMass.x
                y4 = f.CenterOfMass.y
                Vu_df[col] = ""
                for combo, forces in combos_load.items():
                    vu, mx, my = [float(force) for force in forces.split(",")]
                    Vu = vu / b0d + (gamma_vx * (mx - vu * (y3 - y1)) * (I33 * (y4 - y3) - I23 * (x4 - x3))) / (I22 * I33 - I23 ** 2) - (gamma_vy * (my - vu * (x3 - x1)) * (I22 * (x4 - x3) - I23 * (y4 - y3))) / (I22 * I33 - I23 ** 2)
                    Vu *= 1000
                    Vu_df.at[combo, col] = Vu
            Vus_df[_id] = Vu_df.max(axis=1)
        Vus_df.loc['Max'] = Vus_df.max()
        for _id, Vu in Vus_df.loc['Max'].items():
            punch = self.punchs[_id]
            punch.Vu = Vu
        return Vus_df, prop_df

    def allowable_shear_stress(self, fc=None):
        fc = self._safe.fc
        Vc_allowable = pd.Series(index=self.columns_number)
        for _id in self.columns_number:
            punch = self.punchs.get(_id, None)
            if punch == None:
                continue
            bx = punch.bx
            by = punch.by
            location = punch.Location
            if not location:
                Vc_allowable[_id] = 1
                continue
            location = location.rstrip('1234').lower()
            b0d = punch.Area
            b0 = punch.b0
            d = punch.d
            ACI2019 = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("apply_aci2019", False)
            Vc_allowable[_id] = allowable_stress(bx, by, location, fc, b0, d, ACI2019)
        return Vc_allowable

    def punch_ratios(self):
        Vus_df, prop_df = self.ultimate_shear_stress()
        Vcs_series = self.allowable_shear_stress()
        df = Vus_df / Vcs_series
        combos = list(df.index)
        for key in self.columns_number:
            punch = self.punchs.get(key, None)
            if not punch:
                continue
            ratios = [f"{r:.2f}" for r in list(df[key])]
            punch.combos_ratio = dict(zip(combos, ratios))
            ratio = punch.combos_ratio["Max"]
            punch.Ratio = ratio
            punch.text.Text = [punch.Location, punch.Ratio]
        df.loc['Combo'] = Vus_df.idxmax()
        df.loc['properties'] = df.columns
        df = df.append(prop_df)
        # insert ratios to Gui
        return df

    @staticmethod
    def __get_color(pref_intity, color=674321151):
        c = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, color)
        r = float((c >> 24) & 0xFF) / 255.0
        g = float((c >> 16) & 0xFF) / 255.0
        b = float((c >> 8) & 0xFF) / 255.0
        return (r, g, b)
