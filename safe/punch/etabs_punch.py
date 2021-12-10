try:
    # from safe.punch.axis import create_grids
    # from safe.punch.punch_funcs import remove_obj
    from safe.punch import beam
    from safe.punch import etabs_foundation
    # from safe.punch import strip
    # from safe.punch.punch import make_punch
except:
    # from axis import create_grids
    # from punch_funcs import remove_obj
    import etabs_foundation
    import beam
    # from punch import make_punch
import Draft
import FreeCAD
import FreeCADGui as Gui
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
        # self.create_foundation()
        # self.create_punches()
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewTop()
        FreeCAD.DraftWorkingPlane.alignToPointAndAxis(
            FreeCAD.Vector(0.0, 0.0, 0.0),
            FreeCAD.Vector(0, 0, 1),
            self.top_of_foundation)

