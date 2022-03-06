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
import DraftVecUtils
import math
from typing import Union


class EtabsPunch(object):
    def __init__(self,
            beam_names : Union[list, bool] = None,
            etabs_model : Union['etabs_obj.EtabsModel' , bool] = None,
            top_of_foundation : float = 0,
            ):
        if etabs_model is None:
            import etabs_obj
            self.etabs = etabs_obj.EtabsModel(backup=False)
        else:
            self.etabs = etabs_model
        self.etabs.set_current_unit('kN', 'mm')
        self.beam_names = beam_names
        self.top_of_foundation = top_of_foundation

    def create_slabs_plan(self,
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

    def create_columns(self):
        # joint_design_reactions = self.etabs.database.get_joint_design_reactions()
        # basepoints_coord_and_dims = self.etabs.database.get_basepoints_coord_and_dims(
        #         joint_design_reactions
        #     )

        columns = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Columns")
        beams = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Beams")
        profiles = {}
        frame_props = self.etabs.SapModel.PropFrame.GetAllFrameProperties()
        section_types_map = {
            1 : ['H', 'IPE'],
            2 : ['U', 'UNP'],
            6 : ['RH', 'BOX'],
            8 : ['R', 'REC'],
            9 : ['C', 'CIRCLE'],
        }
        frames = self.etabs.SapModel.FrameObj.GetAllFrames()
        progressbar = FreeCAD.Base.ProgressIndicator()
        frames_count = frames[0]
        progressbar.start("Importing "+str(frames_count)+" Frame Elements...", frames_count)
        color = (.0, 1.0, 0.0, 0.0)
        for i in range(frames_count):
            progressbar.next(True)
            frame_name = frames[1][i]
            if self.etabs.frame_obj.is_beam(frame_name):
                if frame_name not in self.beam_names:
                    continue
                v1 = FreeCAD.Vector(frames[6][i], frames[7][i], self.top_of_foundation)
                v2 = FreeCAD.Vector(frames[9][i], frames[10][i], self.top_of_foundation)
                beam_name = beam.make_beam(v1, v2)
                beams.addObject(beam_name)
            elif self.etabs.frame_obj.is_column(frame_name):
                p1_name = frames[4][i]
                p2_name = frames[5][i]
                point_name_restraint = self.is_restraint([p1_name, p2_name])
                if not point_name_restraint:
                    continue
                dz = self.top_of_foundation + abs(frames[11][i] - frames[8][i])
                v1 = FreeCAD.Vector(frames[6][i], frames[7][i], self.top_of_foundation)
                v2 = FreeCAD.Vector(frames[9][i], frames[10][i], dz)
                if DraftVecUtils.equals(v1, v2):
                    continue
                label, story, _ = self.etabs.SapModel.FrameObj.GetLabelFromName(frame_name)
                line = Draft.make_line(v1, v2)
                line.Label = f'{label}_{story}_CenterLine'
                line.Label2 = frame_name
                line.recompute()
                section_name = frames[2][i]
                if section_name:
                    section_index = frame_props[1].index(section_name)
                    section_type_num = frame_props[2][section_index]
                    section_type, category = section_types_map.get(section_type_num, ('G', 'Genaral'))
                else:
                    section_type, category = 'None', 'None'
                width = frame_props[4][section_index]
                height = frame_props[3][section_index]
                profile = profiles.get(section_name, None)
                if profile is None:
                    profile = Arch.makeProfile(
                        profile=[
                                0,
                                category,
                                section_name,
                                section_type,
                                width, # T3
                                height, # height
                                frame_props[6][section_index], # TW
                                frame_props[5][section_index], # TF
                                # frame_props[7][section_index], # heightB
                                # frame_props[8][section_index], # TFB
                                ])
                    profiles[section_name] = profile
                    profile.Label = section_name
                structure = Arch.makeStructure(profile)
                structure.IfcType = 'Column'
                structure.PredefinedType = 'COLUMN'
                structure.Label = f'{label}_{story}'
                structure.Label2 = frame_name
                place_the_beam(structure, line)
                columns.addObject(structure)
                # view property of structure
                if FreeCAD.GuiUp:
                    structure.ViewObject.LineWidth = 1
                    structure.ViewObject.PointSize = 1
                    structure.ViewObject.Transparency = 20
                    structure.ViewObject.ShapeColor = color
                    structure.ViewObject.LineColor = color
                    structure.ViewObject.PointColor = color
                    structure.ViewObject.DisplayMode = 'Wireframe'
                    line.ViewObject.LineColor = color
                    line.ViewObject.PointColor = color
                    if section_type not in ('G', 'None'):
                        line.ViewObject.hide()
                    line.ViewObject.LineWidth = 1
                
                rotation = self.etabs.SapModel.FrameObj.GetLocalAxes(frame_name)[0]
                insertion = self.etabs.SapModel.FrameObj.GetInsertionPoint(frame_name)
                x, y = get_xy_cardinal_point(insertion[0], width, height)
                rotation += 90
                structure.AttachmentOffset = FreeCAD.Placement(
                    FreeCAD.Vector(x, y, 0),
                    FreeCAD.Rotation(FreeCAD.Vector(0,0,1),rotation))
                structure.Nodes = [v1, v2]
        progressbar.stop()

    def create_columns_previos(self):
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
            col.recompute()
            col.ViewObject.LineWidth = 1.00
            col.ViewObject.PointSize = 1.00
            col.ViewObject.Transparency = 30

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
    
    def is_restraint(self, points : list):
        for p in points:
            restraint = self.etabs.SapModel.PointObj.GetRestraint(p)[0]
            if restraint[0:3] == (True, True, True):
                return p
        return False 
    
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
        # self.create_slabs_plan()
        try:
            self.create_columns()
        except TypeError:
            pass
        # self.create_foundation()
        # self.create_punches()
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewTop()
        FreeCAD.DraftWorkingPlane.alignToPointAndAxis(
            FreeCAD.Vector(0.0, 0.0, 0.0),
            FreeCAD.Vector(0, 0, 1),
            self.top_of_foundation)


def place_the_beam(beam, line):
    '''arg1= beam, arg2= edge: lay down the selected beam on the selected edge'''
    edge = line.Shape.Edges[0]
    vect=edge.tangentAt(0)
    beam.Placement.Rotation=FreeCAD.Rotation(0,0,0,1)
    rot=FreeCAD.Rotation(beam.Placement.Rotation.Axis,vect)
    beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
    beam.Placement.Base=edge.valueAt(0)
    beam.addExtension("Part::AttachExtensionPython")
    beam.Support=[(line, 'Edge1')]
    beam.MapMode='NormalToEdge'
    beam.MapReversed=True
    beam.Height=edge.Length

def get_xy_cardinal_point(
        cardinal : int,
        width : float,
        height : float,
        ):
    x = y = 0
    if cardinal in (1, 4, 7):
        x = width / 2
    elif cardinal in (3, 6, 9):
        x = - width / 2
    if cardinal in (7, 8, 9):
        y = - height / 2
    elif cardinal in (1, 2, 3):
        y = height / 2
    return x, y