try:
    from safe.punch.axis import create_grids
    # from safe.punch.punch_funcs import remove_obj
    from safe.punch import etabs_foundation
    from safe.punch import rectangle_slab
    from safe.punch.punch import make_punch
except:
    from axis import create_grids
    # from punch_funcs import remove_obj
    import etabs_foundation
    import rectangle_slab
    from punch import make_punch
import Draft
import FreeCAD as App
import FreeCADGui as Gui
from etabs_api import etabs_obj
from typing import Union


class EtabsPunch(object):
    def __init__(self,
            cover : float = 7.5,
            fc : int = 30,
            ):
        self.etabs = etabs_obj.EtabsModel(backup=False)
        self.SapModel = self.etabs.SapModel
        self.cover = cover
        self.fc = fc
        # self.joint_design_reactions = self.etabs.database.get_joint_design_reactions()
        # self.base_columns_summary = self.etabs.database.get_base_column_summary_with_section_dimensions()
        # if filename:
        #     self._safe = safe.Safe(filename)
        #     self.solid_slabs = self._safe.solid_slabs
        #     self.slab_prop_assignment = self._safe.slab_prop_assignment
        #     self.load_combinations = self._safe.load_combinations
        #     self.point_loads = self._safe.points_loads

    def create_vectors(self):
        vectors = {}
        for name in self.joint_design_reactions['UniqueName'].unique():
            x, y, z, _ = self.SapModel.PointObj.GetCoordCartesian(name)
            vectors[name] = App.Vector(round(x, 4), round(y, 4), int(z))
        return vectors

    def create_slabs(self,
        beam_names : Union[list, bool] = None,
        z=0,
        ):
        slabs = {}
        df_beams = self.etabs.database.get_beams_points_xyz(beam_names)
        for i, row in df_beams.iterrows():
            slab_name = row['UniqueName']
            xi, yi = row['xi'], row['yi']
            xj, yj = row['xj'], row['yj']
            v1 = App.Vector(xi, yi, z)
            v2 = App.Vector(xj, yj, z)
            slabs[slab_name] = rectangle_slab.make_rectangle_slab(v1, v2)
        return slabs

    def create_foundation(self,
        beam_names : Union[list, bool] = None,
        z=0,
        ):
        self.create_slabs(beam_names, z)
        etabs_foundation.make_foundation(self.cover, self.fc)


    def create_punches(self):
        # self.bar_label.setText("Creating Punch Objects")
        for f in self.foundation.Faces:
            if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
                foundation_plane = f
                break
        d = self.foundation.BoundBox.ZLength
        cover = 93
        h = d + cover
        fc = self._safe.fc
        foun_obj = foundation.make_foundation(foundation_plane, height=h, cover=cover, fc=fc)

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
            p = make_punch(
                foundation_plane,
                foun_obj,
                bx,
                by,
                center_of_load,
                d,
                )
            # App.ActiveDocument.recompute()
            l = p.Location
            pl = App.Vector(0, 0, 4100)
            t = '0.0'
            version = App.Version()[1]
            if int(version) < 19:
                text = Draft.makeText([t, l], point=pl)
            else:
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