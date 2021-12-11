try:
    # from safe.punch.axis import create_grids
    # from safe.punch.punch_funcs import remove_obj
    from safe.punch import beam
    # from safe.punch import etabs_foundation
    # from safe.punch import strip
    # from safe.punch.column import make_column
except:
    # from axis import create_grids
    # from punch_funcs import remove_obj
    # import etabs_foundation
    import beam
    # from punch import make_punch
import Draft
import FreeCAD
import FreeCADGui as Gui
import Arch
import math
from typing import Union


class EtabsPunch(object):
    def __init__(self,
            beam_names : Union[list, bool] = None,
            etabs_model : Union['etabs_obj.EtabsModel' , bool] = None,
            top_of_foundation : float = 0,
            ):
        if etabs_model is None:
            from etabs_api import etabs_obj
            self.etabs = etabs_obj.EtabsModel(backup=False)
        else:
            self.etabs = etabs_model
        self.etabs.set_current_unit('kN', 'mm')
        self.beam_names = beam_names
        self.top_of_foundation = top_of_foundation

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
            slabs[slab_name] = beam.make_beam(v1, v2)
        return slabs

    # def create_foundation(self,
    #     ):
    #     self.create_slabs_plane()
    #     Load_cases = self.etabs.load_cases.get_loadcase_withtype(1)
    #     self.foundation = etabs_foundation.make_foundation(
    #         self.cover, self.fc, self.height, self.foundation_type, Load_cases, self.top_of_foundation)

    def create_columns(self):
        joint_design_reactions = self.etabs.database.get_joint_design_reactions()
        basepoints_coord_and_dims = self.etabs.database.get_basepoints_coord_and_dims(
                joint_design_reactions
            )
        def make_column(
            bx : float,
            by : float,
            center : FreeCAD.Vector,
            angle : float,
            combos_load : dict,
            ):
            col = Arch.makeStructure(length=bx,width=by,height=4000)
            col.Placement.Base = center
            col.Placement.Rotation.Angle = math.radians(angle)
            if not hasattr(col, "combos_load"):
                col.addProperty(
                    "App::PropertyMap",
                    "combos_load",
                    "Structure",
                    ).combos_load = combos_load
            col.setEditorMode('combos_load', 2)
            return col

        columns = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Columns")
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
            col = make_column(
                bx,
                by,
                center_of_load,
                angle,
                d,
                )
            col.Label = name
            
            columns.addObject(col)
        return columns
    
    
    
    
    
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
        self.create_slabs_plane()
        self.create_columns()
        # self.create_foundation()
        # self.create_punches()
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewTop()
        FreeCAD.DraftWorkingPlane.alignToPointAndAxis(
            FreeCAD.Vector(0.0, 0.0, 0.0),
            FreeCAD.Vector(0, 0, 1),
            self.top_of_foundation)

