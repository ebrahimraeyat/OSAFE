from pathlib import Path
from typing import Union
import math

try:
    from safe.punch import punch_funcs
    import FreeCAD
    import Part
except:
    pass

__all__ = ['FreecadReadwriteModel']


class FreecadReadwriteModel:

    def __init__(
                self,
                output_path : Path = None,
                doc: 'FreeCAD.Document' = None,
                length_unit: str='mm',
                force_unit: str='N',
                ):
        self.output_path = output_path
        if doc is None:
            doc = FreeCAD.ActiveDocument
        self.doc = doc
        self.material_names=[]
        self.last_point_number = 1000000
        self.last_area_number = 1000000
        self.last_line_number = 1000000
        self.length_unit = length_unit
        self.force_unit = force_unit
        self.length_units = self.get_length_units(self.length_unit)
        self.force_units = self.get_force_units(self.force_unit)
        self.table_text = "#TABLE: "
        self.tables_contents = dict()

    def add_import_statements(self):
        s = '''
import xc_base
import geom
import xc
from model import predefined_spaces
from materials import typical_materials
from postprocess import output_handler
from model.boundary_cond import spring_bound_cond as springs

## Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler

modelSpace= predefined_spaces.StructuralMechanics3D(nodes)

### Define k-points.
points= modelSpace.getPointHandler()

### Define polygonal surface
surfaces= modelSpace.getSurfaceHandler()\n
'''
        self.add_content_to_table("Imports", s, False)
        return s
    
    def add_program_control(self):
        s = f'''
# program_name="XCFEM"   version=16.0.2  units="{self.force_unit}, {self.length_unit}, C"   ConcCode="ACI 318-14"\n
'''
        self.add_content_to_table("Program control", s, False)
        return s
    
    def get_tables_contents(self):
        with open(self.output_path, 'r') as reader:
            lines = reader.readlines()
            tables_contents = dict()
            n = len(self.table_text)
            context = ''
            table_key = None
            for line in lines:
                if line.startswith(self.table_text) or "#END TABLE DATA" in line:
                    if table_key and context:
                        tables_contents[table_key] = context
                    context = ''
                    table_key = line[n+1:-2]
                else:
                    context += line
        self.tables_contents = tables_contents
        return tables_contents
    
    def add_content_to_table(self, table_key, content, append=True):
        '''
        if append is True, content add to current content
        '''
        if append:
            curr_content = self.tables_contents.get(table_key, '')
        else:
            curr_content = ''
        self.tables_contents[table_key] = curr_content + content
        return None
    
    def get_force_units(self, force_unit : str):
        '''
        force_unit can be 'N', 'KN', 'Kgf', 'tonf'
        '''
        if force_unit == 'N':
            return dict(N=1, KN=1000, Kgf=9.81, tonf=9810)
        elif force_unit == 'KN':
            return dict(N=.001, KN=1, Kgf=.00981, tonf=9.81)
        elif force_unit == 'Kgf':
            return dict(N=1/9.81, KN=1000/9.81, Kgf=1, tonf=1000)
        elif force_unit == 'tonf':
            return dict(N=.000981, KN=.981, Kgf=.001, tonf=1)
        else:
            raise KeyError

    def get_length_units(self, length_unit : str):
        '''
        length_unit can be 'mm', 'cm', 'm'
        '''
        if length_unit == 'mm':
            return dict(mm=1, cm=10, m=1000)
        elif length_unit == 'cm':
            return dict(mm=.1, cm=1, m=100)
        elif length_unit == 'm':
            return dict(mm=.001, cm=.01, m=1)
        else:
            raise KeyError
        
    def get_point_str(
            self,
            vector: FreeCAD.Vector(0, 0, 0),
            id_: int = 1,
        ):
        '''
        return the string for adding a point to model
        '''
        return f'pt{id_} = points.newPoint(geom.Pos3d({vector.x}, {vector.y}, {vector.z}))\n'       

    def add_columns_points(
        self,
        columns: Union[list, bool]=None,
        ):
        if columns is None:
            columns = []
            for obj in self.doc.Objects:
                if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                    columns.append(obj)
        s = ''
        for col in columns:
            pl = col.Placement.Base
            s += self.get_point_str(pl, col.ID)
        self.add_content_to_table("Column points", s)
        return s
    
    def add_graphic_stuff(self):
        s = '''
oh= output_handler.OutputHandler(modelSpace)

oh.displayBlocks()#setToDisplay= )
oh.displayFEMesh()#setsToDisplay=[])
oh.displayLocalAxes()
# oh.displayLoads()
# oh.displayReactions()
# oh.displayDispRot(itemToDisp='uX')
# oh.displayDispRot(itemToDisp='uY')
# oh.displayDispRot(itemToDisp='uZ')\n
'''
        self.add_content_to_table("Graphic stuff", s, False)
        return s
    
    def write(self):
        if self.tables_contents is None:
            self.get_tables_contents()
        with open(self.output_path, 'w') as writer:
            for table_key, content in self.tables_contents.items():
                writer.write(f'\n\n{self.table_text}"{table_key}"\n')
                writer.write(content)
            writer.write("\n#END TABLE DATA")
        return None

    def add_slabs(self,
        soil_name : str = 'SOIL',
        soil_modulus : float = 2,
        slab_sec_name : Union[str, None] = None,
            ):
        foun = self.doc.Foundation
        # creating concrete material
        self.add_slab_concrete_material(foun=foun)
        # soil_assignment_content = ''
        all_slab_names = []
        # soil_names = []
        # names_props = []
        slab_sec_names = []
        if foun.foundation_type == 'Strip':
            for base_foundation in foun.base_foundations:
                # create slab section
                height_name = int(base_foundation.height.getValueAs('cm'))
                slab_sec_name = f'SLAB{height_name}'
                if slab_sec_name not in slab_sec_names:
                    # define slab concrete material
                    self.add_slab_concrete_material(foun=base_foundation)
                    slab_sec_names.append(slab_sec_name)
                # # create soil
                # ks_name = f"{base_foundation.ks:.2f}"
                # ks = base_foundation.ks
                # soil_name = f'Soil_{ks_name}'
                # if soil_name not in soil_names:
                #     # soil content
                #     names_props.append((soil_name, ks))
                #     soil_names.append(soil_name)
                faces = base_foundation.extended_plan.Faces
                slab_names = []
                for face in faces:
                    points = self.get_sort_points(face.Edges)
                    name = self.add_area_by_coord(points)
                    slab_names.append(name)
                all_slab_names.extend(slab_names)
                # soil_assignment_content +=  self.add_soil_support(
                #     slab_names=slab_names,
                #     soil_name=soil_name,
                #     soil_modulus=None,
                # )
        
        elif foun.foundation_type == 'Mat':
            height_name = int(foun.height.getValueAs('cm'))
            height = int(foun.height.getValueAs(f'{self.length_unit}'))
            slab_sec_name = f'SLAB{height_name}'
            if slab_sec_name not in slab_sec_names:
                # define slab
                self.add_slab_concrete_material(foun=foun)
                slab_sec_names.append(slab_sec_name)
            if foun.split:
                # names_props = [
                #     (soil_name, soil_modulus),
                #     (f'{soil_name}_1.5', soil_modulus * 1.5),
                #     (f'{soil_name}_2', soil_modulus * 2),
                # ]
                area_points = punch_funcs.get_sub_areas_points_from_face_with_scales(
                    foun.plan_without_openings,
                )
                for points in area_points:
                    name = self.add_area_by_coord(points)
                    all_slab_names.append(name)
                # soil_assignment_content = self.add_soil_support(
                #     slab_names=[all_slab_names[-1]],
                #     soil_name=soil_name,
                #     soil_modulus=None,
                # )
                # soil_assignment_content += self.add_soil_support(
                #     slab_names=all_slab_names[:2],
                #     soil_name=f'{soil_name}_2',
                #     soil_modulus=None,
                # )
                # soil_assignment_content += self.add_soil_support(
                #     slab_names=all_slab_names[2:4],
                #     soil_name=f'{soil_name}_1.5',
                #     soil_modulus=None,
                # )
                
            else:
                # names_props = [(soil_name, soil_modulus)]
                edges = foun.outer_wire.Edges
                points = self.get_sort_points(edges)
                name = self.add_area_by_coord(points)
                all_slab_names.append(name)
                # soil_assignment_content = self.add_soil_support(
                #     slab_names=all_slab_names,
                #     soil_name=soil_name,
                #     soil_modulus=None,
                # )
        # for slab in foun.Slabs:
        #     # create concrete
        #     fc_mpa = int(slab.fc.getValueAs("MPa"))
        #     mat_name = f'C{fc_mpa}'
        #     if mat_name not in mat_names:
        #         self.get_concrete_material(mat_name=mat_name, fc_mpa=fc_mpa)
        #         mat_names.append(mat_name)
        #     # create slab section
        #     height_name = int(slab.height.getValueAs('cm'))
        #     height = int(slab.height.getValueAs(f'{self.length_unit}'))
        #     slab_sec_name = f'SLAB{height_name}'
        #     if slab_sec_name not in slab_sec_names:
        #         # define slab
        #         self.create_solid_slab(slab_sec_name, 'Mat', mat_name, height)
        #         slab_sec_names.append(slab_sec_name)
        #     # create soil
        #     ks_name = f"{slab.ks:.2f}"
        #     ks = slab.ks
        #     soil_name = f'Soil_{ks_name}'
        #     if soil_name not in soil_names:
        #         # soil content
        #         names_props.append((soil_name, ks))
        #         soil_names.append(soil_name)
        #     if hasattr(slab, 'plan'):
        #         faces = slab.plan.Shape.Faces
        #     elif hasattr(slab, 'Base'):
        #         faces = slab.Base.Shape.Faces
        #     slab_names = []
        #     for face in faces:
        #         points = self.get_sort_points(face.Edges)
        #         name = self.add_area_by_coord(points)
        #         slab_names.append(name)
        #     all_slab_names.extend(slab_names)
        #     soil_assignment_content +=  self.add_soil_support(
        #         slab_names=slab_names,
        #         soil_name=soil_name,
        #         soil_modulus=None,
        #     )

        # soil_content = self.create_soil_table(names_props)
        # table_key = "SOIL PROPERTIES"
        # self.add_content_to_table(table_key, soil_content)
        # table_key = "SOIL PROPERTY ASSIGNMENTS"
        # self.add_content_to_table(table_key, soil_assignment_content)
        return all_slab_names
    
    def add_mesh_generation(self, slabs):
        s = 'nDiv= 6\n'
        for slab in slabs:
            s += f'{slab}.setNDiv(nDiv)\n'
        s += "meshSet= modelSpace.defSet('meshSet')\n"
        for slab in slabs:
            s += f'meshSet.surfaces.append({slab})\n'
        s += '''
meshSet.useGmsh= True
meshSet.genMesh(xc.meshDir.I)
'''
        self.add_content_to_table("Generate mesh", s)
        return s


    def get_sort_points(self,
                edges,
                vector=True,
                last=False,
                sort_edges=True,
                ):
        points = []
        if sort_edges:
            edges = Part.__sortEdges__(edges)
        for e in edges:
            v = e.firstVertex()
            if vector:
                points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
            else:
                points.append(v)
        if last:
            v = e.lastVertex()
            if vector:
                points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
            else:
                points.append(v)
        return points

    def add_area_by_coord(self,
            points : 'Base.Vector',
            # prop_name : Union[str, bool] = None,
            # is_opening : bool = False,
            ):
        nodes = '['
        points_content = ''
        areas_content = ''
        area_name = f'SLAB{self.last_area_number}'
        length_scale = self.length_units.get('mm')
        for point in points:
            point = point * length_scale
            points_content += self.get_point_str(point, self.last_point_number)
            nodes += f'pt{self.last_point_number}.tag,'
            self.last_point_number += 1
        nodes += ']'
        areas_content += f"{area_name}= surfaces.newPolygonalFacePts({nodes})\n"
        self.last_area_number += 1
        table_key = "OBJECT GEOMETRY - POINT COORDINATES"
        self.add_content_to_table(table_key, points_content)
        table_key = "OBJECT GEOMETRY - AREAS 01 - GENERAL"
        self.add_content_to_table(table_key, areas_content)
        # if is_opening:
        #     slab_assignment_content = f"\tArea={area_name}   SlabProp=None   OpeningType=Unloaded\n"
        # else:
        #     slab_assignment_content = f"\tArea={area_name}   SlabProp={prop_name}   OpeningType=None\n"
        # table_key = "SLAB PROPERTY ASSIGNMENTS"
        # self.add_content_to_table(table_key, slab_assignment_content)
        return area_name

    def add_soil_support(
            self,
            slab_names : list,
            soil_modulus : float,
            no_tension: bool=False,
        ):
        soil_modulus *= self.force_units['Kgf'] / self.length_units['cm'] ** 3
        s = ''
        s += "xcTotalSet = preprocessor.getSets.getSet('total')\n"
        s += "foundation_set = preprocessor.getSets.defSet('foundation_set')\n"
        for slab in slab_names:
            s += f"foundation_set.getSurfaces.append({slab})\n"
        s += f'''
## Set the soil parameters.
#cRoz= 2/3.0*math.tan(math.radians(25)) # Foundation base-soil friction coefficient
elasticFoundation= springs.ElasticFoundation(wModulus={soil_modulus}, cRoz= 0, noTensionZ={no_tension})
## Generate springs.
elasticFoundation.generateSprings(foundation_set)
'''
        self.add_content_to_table("Elastic foundation", s)
        return s
    
    @staticmethod
    def get_vertex_from_point(point):
        return Part.Vertex(point.x, point.y, point.z)
        
    def add_slab_concrete_material(self,
            mat_name = '',
            fc_mpa = 0,
            weight = 2400,
            height = 200,
            foun = None,
            ):
        if foun is not None:
            fc_mpa = int(foun.fc.getValueAs("MPa"))
            mat_name = f'C{fc_mpa}'
            height = foun.height.getValueAs("mm")
            height = height * self.length_units["mm"]
        if mat_name in self.material_names:
            return "", ""
        self.material_names.append(mat_name)
        # fc = fc_mpa * self.force_units['N'] / self.length_units['mm'] ** 2
        
        # A = 9.9E-06
        unit_weight = weight * self.force_units['Kgf'] / self.length_units['m'] ** 3
        if weight == 0:
            Ec_mpa = .043 * 2400 ** 1.5 * math.sqrt(fc_mpa)
        else:
            Ec_mpa = .043 * weight ** 1.5 * math.sqrt(fc_mpa)
        Ec = Ec_mpa * self.force_units['N'] / self.length_units['mm'] ** 2
        s1 = f'''
{mat_name} = typical_materials.defElasticMembranePlateSection(preprocessor, "{mat_name}",E={Ec},nu=0.3,rho={unit_weight},h={height})\n
'''
        s2 = f'''
seedElemHandler= preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultMaterial= {mat_name}.name
elem= seedElemHandler.newElement("ShellMITC4",xc.ID([0,0,0,0]))\n
'''
        self.add_content_to_table("Slab Concrete material", s1)
        self.add_content_to_table("Shell element", s2, False)
        return s1, s2

