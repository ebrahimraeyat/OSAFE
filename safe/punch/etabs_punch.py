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

from safe.punch import punch_funcs


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

    def create_columns(self,
            import_beams : bool = True,
            ):
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
        for i in range(frames_count):
            progressbar.next(True)
            frame_name = frames[1][i]
            if import_beams and frame_name in self.beam_names:
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
                    section_type, category = section_types_map.get(section_type_num, ('R', 'REC'))
                else:
                    section_type, category = 'None', 'None'
                width = frame_props[4][section_index]
                height = frame_props[3][section_index]
                profile = profiles.get(section_name, None)
                if profile is None:
                    if section_type == 'C':
                        profile = Draft.make_circle(width / 2)
                    else:
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
                    punch_funcs.format_view_object(
                    obj=structure,
                    shape_color_entity="column_shape_color",
                    line_width_entity="column_line_width",
                    transparency_entity="column_transparency",
                    display_mode_entity="column_display_mode",
                    line_color_entity="column_line_color",
                    )
                    punch_funcs.format_view_object(
                    obj=line,
                    shape_color_entity="column_shape_color",
                    line_width_entity="column_line_width",
                    transparency_entity="column_transparency",
                    display_mode_entity="column_display_mode",
                    line_color_entity="column_line_color",
                    )
                    # line.ViewObject.PointSize = 6
                    # if section_type not in ('G', 'None') and import_beams:
                    #     line.ViewObject.hide()
                    # if not import_beams:
                    #     structure.ViewObject.hide()
                
                rotation = self.etabs.SapModel.FrameObj.GetLocalAxes(frame_name)[0]
                insertion = self.etabs.SapModel.FrameObj.GetInsertionPoint(frame_name)
                x, y = get_xy_cardinal_point(insertion[0], width, height)
                rotation += 90
                structure.AttachmentOffset = FreeCAD.Placement(
                    FreeCAD.Vector(x, y, 0),
                    FreeCAD.Rotation(FreeCAD.Vector(0,0,1),rotation))
                structure.Nodes = [v1, v2]
        progressbar.stop()
        return columns

    def import_load_combos(self,
        columns : Union[FreeCAD.DocumentObjectGroup, bool, list] = None,
        ):
        
        joint_design_reactions = self.etabs.database.get_all_joint_design_reactions()
        doc = FreeCAD.ActiveDocument
        if columns is None:
            if hasattr(doc, 'Columns') and hasattr(doc.Columns, 'Group'):
                columns = doc.Columns.Group
            else:
                columns = []
                for obj in doc.Objects:
                    if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                        columns.append(obj)
        elif isinstance(columns, FreeCAD.DocumentObjectGroup):
            columns = columns.Group
        for col in columns:
            label, story = col.Label.split('_')
            name = self.etabs.SapModel.FrameObj.GetNameFromLabel(label, story)[0]
            type_ = self.etabs.frame_obj.get_design_procedure(name)
            points = self.etabs.SapModel.FrameObj.GetPoints(name)[:-1]
            point_reaction = self.is_restraint(points)
            if point_reaction is None:
                continue
            if type_ in ('concrete', 'steel'):
                combos = FreeCAD.ActiveDocument.Meta[f'{type_}_load_combinations']
                combos = combos.split(',')
                filt = (joint_design_reactions['UniqueName'] == point_reaction) & (joint_design_reactions['OutputCase'].isin(combos))
                d = {}
                df = joint_design_reactions.loc[filt]
                for _, row2 in df.iterrows():
                    combo = row2['OutputCase']
                    steptype = row2['StepType']
                    combo_name = f'{combo} {steptype}'
                    F = row2['FZ']
                    mx = row2['MX']
                    my = row2['MY']
                    d[combo_name] = f"{F}, {mx}, {my}"
                if not hasattr(col, "combos_load"):
                    col.addProperty(
                        "App::PropertyMap",
                        "combos_load",
                        "Structure",
                        ).combos_load = d
                col.setEditorMode('combos_load', 2)
                col.recompute() 

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

    def import_data(
            self,
            import_load_combos : bool = True,
            import_beams : bool = True,
        ):
        if FreeCAD.ActiveDocument is None:
            name = self.etabs.get_file_name_without_suffix()
            FreeCAD.newDocument(name)
        # self.create_slabs_plan()
        try:
            columns = self.create_columns(import_beams)
        except TypeError:
            pass
        if FreeCAD.GuiUp:
            Gui.SendMsgToActiveView("ViewFit")
            Gui.activeDocument().activeView().viewTop()
        if hasattr(FreeCAD, 'DraftWorkingPlane'):
            FreeCAD.DraftWorkingPlane.alignToPointAndAxis(
                FreeCAD.Vector(0.0, 0.0, 0.0),
                FreeCAD.Vector(0, 0, 1),
                self.top_of_foundation)
        if import_load_combos:
            self.import_load_combos()
        FreeCAD.ActiveDocument.recompute()
        Gui.Selection.clearSelection()

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
    if FreeCAD.GuiUp:
        col.ViewObject.LineWidth = 1.00
        col.ViewObject.PointSize = 1.00
        col.ViewObject.Transparency = 30
    return col

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