from math import sqrt
import Draft
import Arch
import Part
import FreeCAD as App
import FreeCADGui as Gui
import pandas as pd
from safe.punch import safe
from safe.punch.allowableStress import allowable_stress
from safe.punch.punch import _Punch, _ViewProviderPunch
from safe.punch.axis import create_grids


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
            self.removeSplitter = True

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
            areas[key] = Draft.makeWire(points, closed=True, face=True, support=None)
        return areas

    def create_column(self, point_loads_prop):
        self.bar_label.setText("Creating columns Geometry")
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
        self.bar_label.setText("Creating structures Geometry")
        areas_thickness = self._safe.get_thickness(areas)
        structures = {}
        for key, area in areas.items():
            thickness = areas_thickness[key] - 93
            structures[key] = Arch.makeStructure(area, height=thickness)
            Draft.autogroup(structures[key])
            Draft.move(structures[key], App.Vector(0, 0, -thickness), copy=False)
        return structures

    def create_fusion(self, structures, doc):
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
        self.bar_label.setText("Creating Foundation Geometry")
        if not self.removeSplitter:
            foun = doc.addObject('Part::Feature', 'Foun')
            foun.Shape = fusion.Shape
            return foun
        foun = doc.addObject('Part::Feature', 'Foun')
        foun.Shape = fusion.Shape.removeSplitter()
        doc.removeObject(fusion.Label)
        # gui.getObject(fusion.Name).Visibility = False
        return foun

    def create_3D_column(self, columns):
        self.bar_label.setText("Creating 3D Columns")
        for key, area in columns.items():
            col = Part.makeBox(area.Length, area.Height, 4000, area.Placement.Base)
            try:
                self.punchs[key].Shape = col
            except KeyError:
                pass
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

    def create_column_offset(self, column_areas, gui):
        self.bar_label.setText("Creating offset of d/2 Geometry")
        offset_structures = {}
        d = self._safe.max_thickness
        for key, value in column_areas.items():
            offset_area = Draft.offset(value, App.Vector(0.0, -(d - 93) / 2, 0), copy=True, occ=False)
            offset_structure = Arch.makeStructure(offset_area, height=d)
            Draft.autogroup(offset_structure)
            Draft.move(offset_structure, App.Vector(0, 0, -d), copy=False)
            offset_structures[key] = offset_structure
            gui.getObject(offset_structure.Name).Visibility = False
        return offset_structures

    def get_intersections_areas(self, obj1, obj2):
        outer = obj1.Shape.cut(obj2.Shape)
        inner = obj1.Shape.common(obj2.Shape)
        doc = obj2.Document
        # doc.removeObject(obj2.Label)
        faces_outer = outer.Faces
        faces_inner = inner.Faces
        intersection_faces = []
        for fo in faces_outer:
            for fi in faces_inner:
                if -0.01 < fo.Area - fi.Area < 0.01:
                    if len(fo.Vertexes) == len(fi.Vertexes):
                        no_same_V = 0
                        for vo in fo.Vertexes:
                            for vi in fi.Vertexes:
                                if -.01 < vo.X - vi.X < .01 and -.01 < vo.Y - vi.Y < .01 and -.01 < vo.Z - vi.Z < .01:
                                    no_same_V = no_same_V + 1
                            if no_same_V == len(fo.Vertexes):
                                intersection_faces.append(fo)
        return intersection_faces

    def get_punch_faces(self, foun, offset_structures):
        punch_faces = {}
        self.bar_label.setText("Get Punch Faces")
        i = 1
        for key, value in offset_structures.items():
            punch_faces[key] = self.get_intersections_areas(foun, value)
            self.progressbar.setValue(100 * i / len(self.columns_number))
            i += 1
        return punch_faces

    def shell_center_of_mass(self, faces):
        '''
        give a shell and return center of mass coordinate
        in (x, y, z)
        '''
        sorat_x = 0
        sorat_y = 0
        sorat_z = 0
        makhraj = 0

        for f in faces:
            f = f.Shape
            area = f.Area
            x = f.CenterOfMass.x
            y = f.CenterOfMass.y
            z = f.CenterOfMass.z
            sorat_x += area * x
            sorat_y += area * y
            sorat_z += area * z
            makhraj += area
        if makhraj == 0:
            return None
        return (sorat_x / makhraj, sorat_y / makhraj, sorat_z / makhraj)

    def location_of_column(self, faces):
        faces_normals = {'x': [], 'y': []}
        for f in faces:
            normal = f.normalAt(0, 0)
            normal_x = normal.x
            normal_y = normal.y
            if normal_x:
                if not normal_x in faces_normals['x']:
                    faces_normals['x'].append(normal_x)
            if normal_y:
                if not normal_y in faces_normals['y']:
                    faces_normals['y'].append(normal_y)
        if not (faces_normals['x'] and faces_normals['y']):
            return None
        no_of_faces = len(faces_normals['x'] + faces_normals['y'])
        if no_of_faces == 2:
            signx = faces_normals['x'][0] > 0
            signy = faces_normals['y'][0] > 0
            if not signy:
                if not signx:
                    return 'Corner1'
                elif signx:
                    return 'Corner2'
            elif signy:
                if signx:
                    return 'Corner3'
                elif not signx:
                    return 'Corner4'
            else:
                return 'Corner'
        elif no_of_faces == 3:
            sumx = sum(faces_normals['x'])
            sumy = sum(faces_normals['y'])
            if sumx == 0:
                if sumy == -1:
                    return 'Edge1'
                elif sumy == 1:
                    return 'Edge3'
            elif sumy == 0:
                if sumx == 1:
                    return 'Edge2'
                elif sumx == -1:
                    return 'Edge4'
            else:
                return 'Edge'
        else:
            return 'Interier'

    def loacation_of_columns(self):
        self.bar_label.setText("Obtain Location of Columns")
        locations = {}
        for key, value in self.punch_faces.items():
            locations[key] = self.location_of_column(value)
        return locations

    def create_punches(self):
        self.bar_label.setText("Creating Punch Objects")
        punchs = {}
        fc = self._safe.fc
        for key in self.columns_number:
            intersection_faces = self.punch_faces.get(key, None)
            if intersection_faces is None:
                continue
            location = self.locations.get(key, None)
            if location is None:
                continue
            p = App.ActiveDocument.addObject("Part::FeaturePython", "Punch")
            _Punch(p)
            _ViewProviderPunch(p.ViewObject)
            value = self._safe.point_loads[key]
            p.bx = value['xdim']
            p.by = value['ydim']
            faces = []
            for f in intersection_faces:
                face = App.ActiveDocument.addObject("Part::Feature", "face")
                face.Shape = f
                faces.append(face)
            p.faces = faces
            p.Location = self.locations[key]
            p.fc = int(fc)
            length = p.bx * 1.5
            height = p.by * 1.5
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
        b = self.foundation.Shape.BoundBox
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
        doc = App.ActiveDocument
        gui = Gui.ActiveDocument
        self.obj_geom_points = self.create_vectors(self._safe.obj_geom_points)
        obj_geom_areas = self.create_areas(self._safe.obj_geom_areas)
        self.obj_geom_point_loads = self.create_column(self._safe.point_loads)
        self.columns_number = list(self._safe.point_loads.keys())
        self.structures = self.create_structures(obj_geom_areas)
        del obj_geom_areas
        fusion = self.create_fusion(self.structures, doc)
        doc.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        self.foundation = self.create_foundation(fusion, doc, gui)
        # if fusion.Label:
        #     import OpenSCADUtils
        #     OpenSCADUtils.removesubtree(App.ActiveDocument.getObjectsByLabel(fusion.Label))
        del fusion
        self.offset_structures = self.create_column_offset(self.obj_geom_point_loads, gui)
        doc.recompute()
        self.punch_faces = self.get_punch_faces(self.foundation, self.offset_structures)
        doc.recompute()
        self.grid_lines()
        self.locations = self.loacation_of_columns()
        self.punchs = self.create_punches()
        self.create_3D_column(self.obj_geom_point_loads)
        doc.recompute()
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
            point = self._safe.obj_geom_points[_id]
            x1, y1 = point.x, point.y
            prop_df[_id] = [I22, I33, I23, punch.Location, b0d, gamma_vx, gamma_vy, bx, by, x1, y1]
            x3, y3 = punch.x3, punch.y3
            combos_load = self._safe.points_loads_combinations[self._safe.points_loads_combinations['Point'] == _id]
            combos_load.set_index('Combo', inplace=True)
            Vu_df = pd.DataFrame(index=combos)
            for col, f in enumerate(punch.faces):
                f = f.Shape
                x4 = f.CenterOfMass.x
                y4 = f.CenterOfMass.y
                Vu_df[col] = ""
                for combo in combos:
                    _, vu, mx, my = list(combos_load.loc[combo])
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
        df.loc['Combo'] = Vus_df.idxmax()
        df.loc['properties'] = df.columns
        df = df.append(prop_df)
        # insert ratios to Gui
        for key in self.columns_number:
            punch = self.punchs.get(key, None)
            if not punch:
                continue
            ratio = df[key]['Max']
            t = f"{ratio:.2f}"
            punch.Ratio = t
            punch.text.Text = [punch.Location, punch.Ratio]
        return df

    @staticmethod
    def __get_color(pref_intity, color=674321151):
        c = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetUnsigned(pref_intity, color)
        r = float((c >> 24) & 0xFF) / 255.0
        g = float((c >> 16) & 0xFF) / 255.0
        b = float((c >> 8) & 0xFF) / 255.0
        return (r, g, b)
