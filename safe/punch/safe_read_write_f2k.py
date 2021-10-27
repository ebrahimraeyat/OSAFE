from pathlib import Path
from typing import Union
import math


if __name__ == '__main__':
    import sys
    FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
    sys.path.append(FREECADPATH)
try:
    import FreeCAD
    import Part
    from safe.punch import punch_funcs
except:
    pass

__all__ = ['Safe', 'FreecadReadwriteModel']


class Safe():
    def __init__(self,
            input_f2k_path : Path = None,
            output_f2k_path : Path = None,
        ) -> None:
        self.input_f2k_path = input_f2k_path
        if output_f2k_path is None:
            output_f2k_path = input_f2k_path
        self.output_f2k_path = output_f2k_path
        self.__file_object = None
        self.tables_contents = None

    def __enter__(self):
        self.__file_object = open(self.input_f2k_path, 'r')
        return self.__file_object

    def __exit__(self, type, val, tb):
        self.__file_object.close()

    def get_tables_contents(self):
        with open(self.input_f2k_path, 'r') as reader:
            lines = reader.readlines()
            tables_contents = dict()
            n = len("TABLE:  ")
            contex = ''
            table_key = None
            for line in lines:
                if line.startswith("TABLE:"):
                    if table_key and contex:
                        tables_contents[table_key] = contex
                    contex = ''
                    table_key = line[n+1:-2]
                else:
                    contex += line
        self.tables_contents = tables_contents
        return tables_contents

    def add_content_to_table(self, table_key, content):
        curr_content = self.tables_contents.get(table_key, '')
        self.tables_contents[table_key] = curr_content + content
        return None

    def force_length_unit(self,
        content : Union[str, bool] = None,
        ):
        if content is None:
            if self.tables_contents is None:
                self.get_tables_contents()
            table_key = "PROGRAM CONTROL"
            content = self.tables_contents.get(table_key, None)
            if content is None:
                return
        label = 'CurrUnits="'
        init_curr_unit = content.find(label)
        init_unit_index = init_curr_unit + len(label)
        end_unit_index = content[init_unit_index:].find('"') + init_unit_index
        force, length, _ = content[init_unit_index: end_unit_index].split(', ')
        self.force_unit, self.length_unit = force, length
        self.force_units = self.get_force_units(self.force_unit)
        self.length_units = self.get_length_units(self.length_unit)
        return force, length

    def write(self):
        if self.tables_contents is None:
            self.get_tables_contents()
        with open(self.output_f2k_path, 'w') as writer:
            for table_key, content in self.tables_contents.items():
                writer.write(f'\n\nTABLE:  "{table_key}"\n')
                writer.write(content)
            writer.write("\nEND TABLE DATA")
        return None

    def get_force_units(self, force_unit : str):
        '''
        force_unit can be 'N', 'kN', 'Kgf', 'tonf'
        '''
        if force_unit == 'N':
            return dict(N=1, kN=1000, Kgf=9.81, tonf=9810)
        elif force_unit == 'kN':
            return dict(N=.001, kN=1, Kgf=.00981, tonf=9.81)
        elif force_unit == 'Kgf':
            return dict(N=1/9.81, kN=1000/9.81, Kgf=1, tonf=1000)
        elif force_unit == 'tonf':
            return dict(N=.000981, kN=.981, Kgf=.001, tonf=1)
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

class FreecadReadwriteModel():

    def __init__(
                self,
                input_f2k_path : Path,
                output_f2k_path : Path = None,
                doc: 'App.Document' = None,
                ):
        if output_f2k_path is None:
            output_f2k_path = input_f2k_path
        self.safe = Safe(input_f2k_path, output_f2k_path)
        self.safe.get_tables_contents()
        self.safe.force_length_unit()
        self.force_unit = self.safe.force_unit
        self.length_unit = self.safe.length_unit
        if doc is None:
            doc = FreeCAD.ActiveDocument
        self.doc = doc
        self.last_point_number = 1000
        self.last_area_number = 1000

    def export_freecad_slabs(self,
        split_mat : bool = True,
        soil_name : str = 'SOIL',
        soil_modulus : float = 2,
        slab_sec_name : Union[str, None] = None,
            ):
        
        foun = self.doc.Foundation
        if slab_sec_name is None:
            foun_height = int(foun.height.getValueAs(f'{self.length_unit}'))
            slab_sec_name = f'SLAB{foun_height}'
        # creating concrete material
        table_key = "MATERIAL PROPERTIES 01 - GENERAL"
        name = int(foun.fc.getValueAs('N/(mm^2)'))
        mat_name = f'C{name}'
        material_content = f'Material={mat_name}   Type=Concrete\n'
        self.safe.add_content_to_table(table_key, material_content)
        table_key = "MATERIAL PROPERTIES 03 - CONCRETE"
        A = 9.9E-06
        w = 2400
        unit_weight = w * self.safe.force_units['Kgf'] / self.safe.length_units['m'] ** 3
        fc = foun.fc.getValueAs('MPa') * self.safe.force_units['N'] / self.safe.length_units['mm'] ** 2
        Ec = .043 * w ** 1.5 * math.sqrt(foun.fc.getValueAs('MPa'))
        mat_prop_content = f'Material={mat_name}   E={Ec}   U=0.2   A={A}   UnitWt={unit_weight}   Fc={fc}   LtWtConc=No   UserModRup=No\n'
        self.safe.add_content_to_table(table_key, mat_prop_content)
        # define slab
        table_key = "SLAB PROPERTIES 01 - GENERAL"
#    Slab=COL   Type=Stiff   ThickPlate=Yes   Color=Cyan   Notes="Added 1/31/2017 11:08:53 PM"   GUID=16338132-0503-48a9-b221-6a7c72b6c716
        slab_general_content = f'Slab={slab_sec_name}   Type=Mat   ThickPlate=Yes\n'
        self.safe.add_content_to_table(table_key, slab_general_content)
        table_key = "SLAB PROPERTIES 02 - SOLID SLABS"
        slab_prop_content = f'Slab={slab_sec_name}   Type=Mat   MatProp={mat_name}   Thickness={foun_height}   Ortho=No\n'
        self.safe.add_content_to_table(table_key, slab_prop_content)
        slab_names = []
        if foun.foundation_type == 'Strip':
            # soil content
            names_props = [(soil_name, soil_modulus)]
            soil_content = self.create_soil_table(names_props)
            points = punch_funcs.get_points_of_foundation_plan_and_holes(foun)
            name = self.create_area_by_coord(points[0], slab_sec_name)
            slab_names.append(name)
            soil_assignment_content =  self.export_freecad_soil_support(
                slab_names=slab_names,
                soil_name=soil_name,
                soil_modulus=None,
            )
            for pts in points[1:]:
                self.create_area_by_coord(pts, is_opening=True)
        
        elif foun.foundation_type == 'Mat':
            if split_mat:
                names_props = [
                    (soil_name, soil_modulus),
                    (f'{soil_name}_1.5', soil_modulus * 1.5),
                    (f'{soil_name}_2', soil_modulus * 2),
                ]
                soil_content = self.create_soil_table(names_props)
                area_points = punch_funcs.get_sub_areas_points_from_face_with_scales(
                    foun.plane_without_openings,
                )
                for points in area_points:
                    name = self.create_area_by_coord(points, slab_sec_name)
                    slab_names.append(name)
                soil_assignment_content = self.export_freecad_soil_support(
                    slab_names=[slab_names[-1]],
                    soil_name=soil_name,
                    soil_modulus=None,
                )
                soil_assignment_content += self.export_freecad_soil_support(
                    slab_names=slab_names[:2],
                    soil_name=f'{soil_name}_2',
                    soil_modulus=None,
                )
                soil_assignment_content += self.export_freecad_soil_support(
                    slab_names=slab_names[2:4],
                    soil_name=f'{soil_name}_1.5',
                    soil_modulus=None,
                )
                
            else:
                names_props = [(soil_name, f'{soil_modulus}')]
                soil_content = self.create_soil_table(names_props)
                edges = foun.plane_without_openings.Edges
                points = self.get_sort_points(edges)
                name = self.create_area_by_coord(points, slab_sec_name)
                slab_names.append(name)
                soil_assignment_content = self.export_freecad_soil_support(
                    slab_names=slab_names,
                    soil_name=soil_name,
                    soil_modulus=None,
                )
        table_key = "SOIL PROPERTIES"
        self.safe.add_content_to_table(table_key, soil_content)
        table_key = "SOIL PROPERTY ASSIGNMENTS"
        self.safe.add_content_to_table(table_key, soil_assignment_content)
        return slab_names

    def get_sort_points(self, edges, vector=True):
        points = []
        edges = Part.__sortEdges__(edges)
        for e in edges:
            v = e.firstVertex()
            if vector is True:
                points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
            else:
                points.append(v)
        return points

    def create_area_by_coord(self,
            points : 'Base.Vector',
            prop_name : Union[str, bool] = None,
            is_opening : bool = False,
            ):
        n = len(points)
        nodes = []
        points_content = ''
        area_name = self.last_area_number
        areas_content = f"\tArea={area_name}   NumPoints={n}"
        length_scale = self.safe.length_units.get(self.length_unit)
        for i, point in enumerate(points, start=1):
            x = point.x * length_scale
            y = point.y * length_scale
            z = point.z * length_scale
            if i % 4 == 0:
                points_content += f"Point={self.last_point_number}   GlobalX={x}   GlobalY={y}   GlobalZ={z}   SpecialPt=No\n"
                nodes.append(self.last_point_number)
                self.last_point_number += 1
                if i == 4:
                    areas_content += f"\tPoint1={nodes[0]}   Point2={nodes[1]}   Point3={nodes[2]}   Point4={nodes[3]}\n"
                else:
                    areas_content += f"\tArea={area_name}   Point1={nodes[0]}   Point2={nodes[1]}   Point3={nodes[2]}   Point4={nodes[3]}\n"
                nodes = []
            else:
                points_content += f"Point={self.last_point_number}   GlobalX={x}   GlobalY={y}   GlobalZ={z}   SpecialPt=No\n"
                nodes.append(self.last_point_number)
                self.last_point_number += 1
        for i, node in enumerate(nodes, start=1):
            if i == 1 and n > 4:
                areas_content += f"Area={area_name}"
            areas_content += f"\tPoint{i}={node}   "
        self.last_area_number += 1
        areas_content += '\n'
        table_key = "OBJECT GEOMETRY - POINT COORDINATES"
        self.safe.add_content_to_table(table_key, points_content)
        table_key = "OBJECT GEOMETRY - AREAS 01 - GENERAL"
        self.safe.add_content_to_table(table_key, areas_content)
        if is_opening:
            slab_assignment_content = f"\tArea={area_name}   SlabProp=None   OpeningType=Unloaded\n"
        else:
            slab_assignment_content = f"\tArea={area_name}   SlabProp={prop_name}   OpeningType=None\n"
        table_key = "SLAB PROPERTY ASSIGNMENTS"
        self.safe.add_content_to_table(table_key, slab_assignment_content)

        return area_name

    def export_freecad_openings(self, doc : 'App.Document' = None):
        # self.etabs.set_current_unit('kN', 'mm')
        # if doc is None:
        #     doc = FreeCAD.ActiveDocument
        foun = doc.Foundation
        if foun.foundation_type == 'Strip':
            return
        openings = foun.openings
        for opening in openings:
            points = opening.points
            self.create_area_by_coord(points, is_opening=True)
            # n = len(points)
            # xs = [p.x for p in points]
            # ys = [p.y for p in points]
            # zs = [p.z for p in points]
            # ret = self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)
            # name = ret[3]
            # self.SapModel.AreaObj.SetOpening(name, True)

    def export_freecad_strips(self, doc : 'App.Document' = None):
        self.etabs.set_current_unit('kN', 'mm')
        if doc is None:
            doc = FreeCAD.ActiveDocument
        foun = doc.Foundation
        data = []
        if foun.foundation_type == 'Strip':
            slabs = foun.tape_slabs
            i = j = 0
            for slab in slabs:
                p1 = slab.start_point
                p2 = slab.end_point
                p = self.SapModel.PointObj.AddCartesian(p1.x, p1.y, p1.z)
                p1_name = p[0]
                p = self.SapModel.PointObj.AddCartesian(p2.x, p2.y, p2.z)
                p2_name = p[0]
                swl = ewl = slab.width.Value / 2 + slab.offset
                swr = ewr = slab.width.Value / 2 - slab.offset
                dx = abs(p1.x - p2.x)
                dy = abs(p1.y - p2.y)
                if dx > dy:
                    layer = 'A'
                    i += 1
                    name = f'CS{layer}{i}'
                else:
                    layer = 'B'
                    j += 1
                    name = f'CS{layer}{j}'
                data.extend((
                    name,
                    '1',
                    f'{p1_name}',
                    f'{p2_name}',
                    f'{swl}',
                    f'{swr}',
                    f'{ewl}',
                    f'{ewr}',
                    'NO',
                    f'{layer}',
                    ))
        table_key = 'Strip Object Connectivity'
        fields = ['Name', 'NumSegs', 'StartPoint', 'EndPoint', 'WStartLeft',
            'WStartRight', 'WEndLeft', 'WEndRight', 'AutoWiden', 'Layer']
        if self.etabs.software == 'ETABS':
            fields.insert(1, 'Story')
        assert len(fields) == len(data) / len(slabs)
        self.etabs.database.apply_data(table_key, data, fields)

    def export_freecad_stiff_elements(self, doc : 'App.Document' = None):
        self.etabs.set_current_unit('kN', 'mm')
        self.SapModel.PropMaterial.SetMaterial('CONCRETE_ZERO', 2)
        self.SapModel.PropMaterial.SetWeightAndMass('CONCRETE_ZERO', 1, 0)
        self.SapModel.PropMaterial.SetWeightAndMass('CONCRETE_ZERO', 2, 0)
        self.SapModel.PropArea.SetSlab('COL_STIFF', 2, 2, 'CONCRETE_ZERO', 1500)

        if doc is None:
            doc = FreeCAD.ActiveDocument
        for o in doc.Objects:
            if (hasattr(o, "Proxy") and 
                hasattr(o.Proxy, "Type") and 
                o.Proxy.Type == "Punch"
                ):
                points = self.get_sort_points(o.rect.Edges)
                self.create_area_by_coord(points, prop_name='COL_STIFF')
    
    def export_freecad_wall_loads(self, doc : 'App.Document' = None):
        if doc is None:
            doc = FreeCAD.ActiveDocument
        for o in doc.Objects:
            if (hasattr(o, "Proxy") and 
                hasattr(o.Proxy, "Type") and 
                o.Proxy.Type == "Wall"
                ):
                mass_per_area = o.weight
                height = o.Height.Value / 1000
                p1 = o.Base.start_point
                p2 = o.Base.end_point
                self.etabs.set_current_unit('kgf', 'mm')
                frame = self.SapModel.FrameObj.AddByCoord(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z,'', 'None')
                name = frame[0]
                loadpat = self.etabs.load_patterns.get_special_load_pattern_names(1)[0]
                self.etabs.set_current_unit('kgf', 'm')
                self.etabs.frame_obj.assign_gravity_load_from_wall(
                    name = name,
                    loadpat = loadpat,
                    mass_per_area = mass_per_area,
                    height = height,
                )

    def export_freecad_soil_support(self,
        slab_names : list,
        soil_name : str = 'SOIL',
        soil_modulus : Union[float, bool] = None,
        ):
        # self.etabs.set_current_unit('kgf', 'cm')
        # if soil_modulus is not None:
        #     self.SapModel.PropAreaSpring.SetAreaSpringProp(
        #         soil_name, 0, 0, soil_modulus , 3)
        soil_assignment_content = ''
        for slab_name in slab_names:
            soil_assignment_content += f"Area={slab_name}   SoilProp={soil_name}\n"
        return soil_assignment_content

    def set_uniform_gravity_load(self,
        area_names : list,
        load_pat : str,
        value : float,
        ) -> None:
        self.etabs.set_current_unit('kgf', 'm')
        for area_name in area_names:
            self.SapModel.AreaObj.SetLoadUniform(
                area_name,
                load_pat,
                -value,
                6,  # Dir
            )
    
    @staticmethod
    def get_vertex_from_point(point):
        return Part.Vertex(point.x, point.y, point.z)

    def create_soil_table(self, soil_prop):
        soil_content = ''
        for name, ks in soil_prop:
            ks *= self.safe.force_units['Kgf'] / self.safe.length_units['cm'] ** 3
            soil_content += f'Soil={name}   Subgrade={ks}   NonlinOpt="Compression Only"\n'
        return soil_content

if __name__ == '__main__':
    import sys
    from pathlib import Path

    FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
    sys.path.append(FREECADPATH)
    import FreeCAD
    if FreeCAD.GuiUp:
        document = FreeCAD.ActiveDocument
    else:
        filename = Path(__file__).absolute().parent.parent / 'test' / 'etabs_api' / 'test_files' / 'freecad' / 'mat.FCStd'
        document= FreeCAD.openDocument(str(filename))
    slabs = document.Foundation.tape_slabs
    openings = document.Foundation.openings

    current_path = Path(__file__).parent
    sys.path.insert(0, str(current_path))
    from etabs_obj import EtabsModel
    etabs = EtabsModel(backup=False, software='SAFE')
    # etabs.area.get_scale_area_points_with_scale(document.Foundation.plane_without_openings)
    SapModel = etabs.SapModel
    ret = etabs.area.export_freecad_slabs(document)
    ret = etabs.area.export_freecad_openings(openings)
    print('Wow')

