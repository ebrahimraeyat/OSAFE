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
import FreeCAD
import FreeCADGui as Gui
from typing import Union


class EtabsPunch(object):
    def __init__(self,
            cover : float = 75,
            fc : int = 30,
            height : int = 800,
            width : int = 1000,
            beam_names : Union[list, bool] = None,
            etabs_model : Union['etabs_obj.EtabsModel' , bool] = None,
            top_of_foundation : float = 0,
            foundation_type : str = 'Strip',
            ):
        if etabs_model is None:
            from etabs_api import etabs_obj
            self.etabs = etabs_obj.EtabsModel(backup=False)
        else:
            self.etabs = etabs_model
        self.etabs.set_current_unit('kN', 'mm')
        self.cover = cover
        self.fc = fc
        self.height = height
        self.width = width
        self.beam_names = beam_names
        self.top_of_foundation = top_of_foundation
        self.foundation_type = foundation_type
        # self.joint_design_reactions = self.etabs.database.get_joint_design_reactions()
        # self.base_columns_summary = self.etabs.database.get_base_column_summary_with_section_dimensions()
        # if filename:
        #     self._safe = safe.Safe(filename)
        #     self.solid_slabs = self._safe.solid_slabs
        #     self.slab_prop_assignment = self._safe.slab_prop_assignment
        #     self.load_combinations = self._safe.load_combinations
        #     self.point_loads = self._safe.points_loads

    # def create_vectors(self):
    #     vectors = {}
    #     for name in self.joint_design_reactions['UniqueName'].unique():
    #         x, y, z, _ = self.SapModel.PointObj.GetCoordCartesian(name)
    #         vectors[name] = FreeCAD.Vector(round(x, 4), round(y, 4), int(z))
    #     return vectors

    def create_slabs_plane(self,
        ):
        slabs = {}
        df_beams = self.etabs.database.get_frame_points_xyz(self.beam_names)
        for _, row in df_beams.iterrows():
            slab_name = row['UniqueName']
            xi, yi = row['xi'], row['yi']
            xj, yj = row['xj'], row['yj']
            v1 = FreeCAD.Vector(xi, yi, self.top_of_foundation)
            v2 = FreeCAD.Vector(xj, yj, self.top_of_foundation)
            slabs[slab_name] = rectangle_slab.make_rectangle_slab(v1, v2, self.width, self.height)
        return slabs

    def create_foundation(self,
        ):
        self.create_slabs_plane()
        Load_cases = self.etabs.load_cases.get_loadcase_withtype(1)
        self.foundation = etabs_foundation.make_foundation(
            self.cover, self.fc, self.height, self.foundation_type, Load_cases)

    def create_punches(self):
        joint_design_reactions = self.etabs.database.get_joint_design_reactions()
        basepoints_coord_and_dims = self.etabs.database.get_basepoints_coord_and_dims(
                joint_design_reactions
            )
        # for f in self.foundation.Shape.Faces:
        #     if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
        #         foundation_plane = f
        #         break
        # self.foundation.plane = foundation_plane
        punches = []
        for _, row in basepoints_coord_and_dims.iterrows():
            name = row['UniqueName']
            bx = float(row['t3'])
            by = float(row['t2'])
            if (not bx > 0) or (not by > 0):
                continue
            angle = float(row['AxisAngle'])
            x = row['x']
            y = row['y']
            # z = row['z']
            d = {}
            df = joint_design_reactions[joint_design_reactions['UniqueName'] == name]
            for _, row2 in df.iterrows():
                combo = row2['OutputCase']
                F = row2['FZ']
                mx = row2['MX']
                my = row2['MY']
                d[combo] = f"{F}, {mx}, {my}"
            center_of_load = FreeCAD.Vector(x, y, self.top_of_foundation)
            p = make_punch(
                # foundation_plane,
                self.foundation,
                bx,
                by,
                center_of_load,
                d,
                angle=angle,
                )
            l = p.Location
            pl = FreeCAD.Vector(0, 0, self.top_of_foundation + 4100)
            t = '0.0'
            version = FreeCAD.Version()[1]
            if int(version) < 19:
                text = Draft.makeText([t, l], point=pl)
            else:
                text = Draft.make_text([t, l], placement=pl)
            p.Ratio = t
            if FreeCAD.GuiUp:
                text.ViewObject.FontSize = 200
            print(text)
            p.text = text
            p.id = name
            punches.append(p)
        return punches

    def grid_lines(self):
        if not FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("draw_grid", True):
            return

        gridLines = self._safe.grid_lines()
        if gridLines is None:
            return
        x_grids = gridLines['x']
        y_grids = gridLines['y']
        b = self.foundation.BoundBox
        create_grids(x_grids, b, 'x')
        create_grids(y_grids, b, 'y')

    def import_data(self):
        name = self.etabs.get_file_name_without_suffix()
        FreeCAD.newDocument(name)
        self.create_foundation()
        self.create_punches()
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewAxonometric()
