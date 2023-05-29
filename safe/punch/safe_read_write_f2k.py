from pathlib import Path
from typing import Union
import math

try:
    import FreeCAD
    import Part
    from safe.punch import punch_funcs
except:
    pass

__all__ = ['Safe', 'Safe12', 'FreecadReadwriteModel']


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
            context = ''
            table_key = None
            for line in lines:
                if line.startswith("TABLE:") or "END TABLE DATA" in line:
                    if table_key and context:
                        tables_contents[table_key] = context
                    context = ''
                    table_key = line[n+1:-2]
                else:
                    context += line
        self.tables_contents = tables_contents
        return tables_contents

    def get_points_coordinates(self,
            content : str = None,
            ) -> dict:
        if content is None:
            content = self.tables_contents["OBJECT GEOMETRY - POINT COORDINATES"]
        lines = content.split('\n')
        points_coordinates = dict()
        for line in lines:
            if not line:
                continue
            line = line.lstrip(' ')
            fields_values = line.split()
            coordinates = []
            for i, field_value in enumerate(fields_values[:-1]):
                if i == 0:
                    point_name = str(field_value.split('=')[1])
                else:
                    value = float(field_value.split('=')[1])
                    coordinates.append(value)
            points_coordinates[point_name] = coordinates
        return points_coordinates

    def is_point_exist(self,
            coordinate : list,
            content : Union[str, bool] = None,
            points_coordinates : Union[bool, dict] = None,
            ):
        if points_coordinates is None:
            points_coordinates = self.get_points_coordinates(content)
        for _id, coord in points_coordinates.items():
            if (
                len(coord) == 3 and
                math.isclose(coord[0], coordinate[0], abs_tol=.001) and
                math.isclose(coord[1], coordinate[1], abs_tol=.001) and
                math.isclose(coord[2], coordinate[2], abs_tol=.001)
                ):
                return _id
        return None
                    
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

    def set_analysis_type(self, is_2d='Yes'):
        table_key =  "ADVANCED MODELING OPTIONS"
        content = f"2DOnly={is_2d}   RigDiaTop=No   NoOffsets=Yes"
        self.add_content_to_table(table_key, content, append=False)
    
    def set_mesh_options(self, mesh_size=300):
        table_key =  "AUTOMATIC SLAB MESH OPTIONS"
        content = f"MeshOpt=Rectangular   Localize=Yes   Merge=Yes   MaxSize={mesh_size * self.length_units.get('mm')}"
        self.add_content_to_table(table_key, content, append=False)

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

class Safe12(Safe):
    def __init__(self,
            input_f2k_path : Path = None,
            output_f2k_path : Path = None,
        ) -> None:
        super().__init__(input_f2k_path, output_f2k_path)
        self.input_f2k_path = input_f2k_path

    def get_tables_contents(self):
        with open(self.input_f2k_path, 'r') as reader:
            lines = reader.readlines()
            tables_contents = dict()
            n = len("$ ")
            context = ''
            table_key = None
            for line in lines:
                if line.startswith("$"):
                    if table_key and context:
                        tables_contents[table_key] = context
                    context = ''
                    table_key = line[n+1:-2]
                else:
                    context += line
        self.tables_contents = tables_contents
        return tables_contents

    def get_points_coordinates(self,
            content : str = None,
            ) -> dict:
        if content is None:
            content = self.tables_contents["POINT COORDINATES"]
        lines = content.split('\n')
        points_coordinates = dict()
        for line in lines:
            if not line:
                continue
            line = line.lstrip('  POINT')
            fields_values = line.split()
            coordinates = []
            for i, field_value in enumerate(fields_values):
                if i == 0:
                    point_name = str(field_value).strip('"')
                else:
                    value = float(field_value)
                    coordinates.append(value)
            points_coordinates[point_name] = coordinates
        return points_coordinates

    def is_point_exist(self,
            coordinate : list,
            content : Union[str, bool] = None,
            ):
        points_coordinates = self.get_points_coordinates(content)
        for id, coord in points_coordinates.items():
            if coord == coordinate:
                return id
        return None
                    
    def force_length_unit(self,
        content : Union[str, bool] = None,
        ):
        with open(self.input_f2k_path, 'r') as reader:
            while True:
                line = reader.readline()
                if 'UNITS' in line:
                    line = line.lstrip('  ')
                    force, length = line.split()[1:]
                    break
        self.force_unit, self.length_unit = force, length
        self.force_units = self.get_force_units(self.force_unit)
        self.length_units = self.get_length_units(self.length_unit)
        return force, length

    def write(self):
        if self.tables_contents is None:
            self.get_tables_contents()
        with open(self.output_f2k_path, 'w') as writer:
            for table_key, content in self.tables_contents.items():
                writer.write(f'\n\n$ "{table_key}"\n')
                writer.write(content)
            writer.write("\n  END\n$ END OF MODEL FILE\n")
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

class FreecadReadwriteModel():

    def __init__(
                self,
                input_f2k_path : Path = None,
                output_f2k_path : Path = None,
                doc: 'App.Document' = None,
                ):
        if doc is None:
            doc = FreeCAD.ActiveDocument
        self.doc = doc
        if not input_f2k_path:
            if hasattr(doc, 'Safe') and hasattr(doc.Safe, 'input'):
                input_f2k_path = Path(doc.Safe.input)
        if not output_f2k_path:
            if hasattr(doc, 'Safe') and hasattr(doc.Safe, 'output'):
                output_f2k_path = Path(doc.Safe.output)
            else:
                output_f2k_path = input_f2k_path
        self.safe = Safe(input_f2k_path, output_f2k_path)
        self.safe.get_tables_contents()
        self.safe.force_length_unit()
        self.force_unit = self.safe.force_unit
        self.length_unit = self.safe.length_unit
        self.last_point_number = 1000
        self.last_area_number = 1000
        self.last_line_number = 1000

    def export_freecad_slabs(self,
        soil_name : str = 'SOIL',
        soil_modulus : float = 2,
        slab_sec_name : Union[str, None] = None,
            ):
        
        foun = self.doc.Foundation
        # creating concrete material
        mat_name = self.create_concrete_material(foun=foun)
        mat_names = [mat_name]
        soil_assignment_content = ''
        all_slab_names = []
        soil_names = []
        names_props = []
        slab_sec_names = []
        
        height_name = int(foun.height.getValueAs('cm'))
        height = round(foun.height.getValueAs(f'{self.length_unit}'), 2)
        if foun.foundation_type == 'Strip':
            for base_foundation in foun.base_foundations:
                # create slab section
                if foun.height == 0:
                    height_name = int(base_foundation.height.getValueAs('cm'))
                    height = round(base_foundation.height.getValueAs(f'{self.length_unit}'), 2)
                slab_sec_name = f'SLAB{height_name}'
                if slab_sec_name not in slab_sec_names:
                    # define slab
                    self.create_solid_slab(slab_sec_name, 'Mat', mat_name, height)
                    slab_sec_names.append(slab_sec_name)
                # create soil
                ks_name = f"{base_foundation.ks:.2f}"
                ks = base_foundation.ks
                soil_name = f'Soil_{ks_name}'
                if soil_name not in soil_names:
                    # soil content
                    names_props.append((soil_name, ks))
                    soil_names.append(soil_name)
                faces = base_foundation.extended_plan.Faces
                slab_names = []
                for face in faces:
                    points = self.get_sort_points(face.Edges)
                    name = self.create_area_by_coord(points, slab_sec_name)
                    slab_names.append(name)
                all_slab_names.extend(slab_names)
                soil_assignment_content +=  self.export_freecad_soil_support(
                    slab_names=slab_names,
                    soil_name=soil_name,
                    soil_modulus=None,
                )
        
        elif foun.foundation_type == 'Mat':
            if foun.height == 0:
                height_name = int(foun.height.getValueAs('cm'))
                height = round(foun.height.getValueAs(f'{self.length_unit}'), 2)
            slab_sec_name = f'SLAB{height_name}'
            if slab_sec_name not in slab_sec_names:
                # define slab
                self.create_solid_slab(slab_sec_name, 'Mat', mat_name, height)
                slab_sec_names.append(slab_sec_name)
            if foun.split:
                names_props = [
                    (soil_name, soil_modulus),
                    (f'{soil_name}_1.5', soil_modulus * 1.5),
                    (f'{soil_name}_2', soil_modulus * 2),
                ]
                area_points = punch_funcs.get_sub_areas_points_from_face_with_scales(
                    foun.plan_without_openings,
                )
                for points in area_points:
                    name = self.create_area_by_coord(points, slab_sec_name)
                    all_slab_names.append(name)
                soil_assignment_content = self.export_freecad_soil_support(
                    slab_names=[all_slab_names[-1]],
                    soil_name=soil_name,
                    soil_modulus=None,
                )
                soil_assignment_content += self.export_freecad_soil_support(
                    slab_names=all_slab_names[:2],
                    soil_name=f'{soil_name}_2',
                    soil_modulus=None,
                )
                soil_assignment_content += self.export_freecad_soil_support(
                    slab_names=all_slab_names[2:4],
                    soil_name=f'{soil_name}_1.5',
                    soil_modulus=None,
                )
                
            else:
                names_props = [(soil_name, soil_modulus)]
                edges = foun.outer_wire.Edges
                points = self.get_sort_points(edges)
                name = self.create_area_by_coord(points, slab_sec_name)
                all_slab_names.append(name)
                soil_assignment_content = self.export_freecad_soil_support(
                    slab_names=all_slab_names,
                    soil_name=soil_name,
                    soil_modulus=None,
                )
        for slab in foun.Slabs:
            # create concrete
            fc_mpa = int(slab.fc.getValueAs("MPa"))
            mat_name = f'C{fc_mpa}'
            if mat_name not in mat_names:
                self.create_concrete_material(mat_name=mat_name, fc_mpa=fc_mpa)
                mat_names.append(mat_name)
            # create slab section
            if foun.height == 0:
                height_name = int(slab.height.getValueAs('cm'))
                height = round(slab.height.getValueAs(f'{self.length_unit}'), 2)
            slab_sec_name = f'SLAB{height_name}'
            if slab_sec_name not in slab_sec_names:
                # define slab
                self.create_solid_slab(slab_sec_name, 'Mat', mat_name, height)
                slab_sec_names.append(slab_sec_name)
            # create soil
            ks_name = f"{slab.ks:.2f}"
            ks = slab.ks
            soil_name = f'Soil_{ks_name}'
            if soil_name not in soil_names:
                # soil content
                names_props.append((soil_name, ks))
                soil_names.append(soil_name)
            if hasattr(slab, 'plan'):
                faces = slab.plan.Shape.Faces
            elif hasattr(slab, 'Base'):
                faces = slab.Base.Shape.Faces
            slab_names = []
            for face in faces:
                points = self.get_sort_points(face.Edges)
                name = self.create_area_by_coord(points, slab_sec_name)
                slab_names.append(name)
            all_slab_names.extend(slab_names)
            soil_assignment_content +=  self.export_freecad_soil_support(
                slab_names=slab_names,
                soil_name=soil_name,
                soil_modulus=None,
            )

        soil_content = self.create_soil_table(names_props)
        table_key = "SOIL PROPERTIES"
        self.safe.add_content_to_table(table_key, soil_content)
        table_key = "SOIL PROPERTY ASSIGNMENTS"
        self.safe.add_content_to_table(table_key, soil_assignment_content)
        return all_slab_names

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
        length_scale = self.safe.length_units.get('mm')
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
        foun = self.doc.Foundation
        if foun.foundation_type == 'Strip':
            return
        openings = foun.openings
        names = []
        for opening in openings:
            points = [v.Point for v in opening.Base.Shape.Vertexes]
            name = self.create_area_by_coord(points, is_opening=True)
            names.append(name)
        return names

    def export_freecad_strips(self):
        point_coords_table_key = "OBJECT GEOMETRY - POINT COORDINATES"
        points_content = ''
        curr_point_content = self.safe.tables_contents.get(point_coords_table_key, '')
        strip_table_key = "OBJECT GEOMETRY - DESIGN STRIPS"
        strip_content = ''
        strip_assign_table_key = "SLAB DESIGN OVERWRITES 01 - STRIP BASED"
        strip_assign_content = ''
        self.create_rebar_material('AIII', 400)
        scale_factor = self.safe.length_units['mm']
        for o in self.doc.Objects:
            if hasattr(o, 'Proxy') and \
                hasattr(o.Proxy, 'Type') and \
                    o.Proxy.Type == 'Strip':
                layer = o.layer
                strip_name = o.Label
                points = o.Base.Points
                sl = o.left_width.Value
                sr = o.right_width.Value
                swl = ewl = sl * scale_factor
                swr = ewr = sr * scale_factor
                placement = o.Placement.Base + o.Base.Placement.Base
                for j, point in enumerate(points):
                    coord = [coord * scale_factor for coord in (point.x + placement.x, point.y + placement.y, point.z)]
                    point_name = self.safe.is_point_exist(coord, curr_point_content + points_content)
                    if point_name is None:
                        points_content += f"Point={self.last_point_number}   GlobalX={coord[0]}   GlobalY={coord[1]}   GlobalZ={coord[2]}   SpecialPt=No\n"
                        point_name = self.last_point_number
                        self.last_point_number += 1
                    if j == 0:
                        strip_content += f'\tStrip={strip_name}   Point={point_name}   GlobalX={coord[0]}   GlobalY={coord[1]}   WALeft={swl}   WARight={swr}   AutoWiden=No\n'
                    elif j == len(points) - 1: # last strip
                        strip_content += f'\tStrip={strip_name}   Point={point_name}   GlobalX={coord[0]}   GlobalY={coord[1]}   WBLeft={ewl}   WBRight={ewr}\n'
                    else:
                        strip_content += f'\tStrip={strip_name}   Point={point_name}   GlobalX={coord[0]}   GlobalY={coord[1]}   WBLeft={ewl}   WBRight={ewr} WALeft={swl}   WARight={swr} \n'
                strip_assign_content += f'\tStrip={strip_name}   Layer={layer}   DesignType=Column   RLLF=1   Design=Yes   IgnorePT=No   RebarMat=AIII   CoverType=Preferences\n'
        self.safe.add_content_to_table(point_coords_table_key, points_content)
        self.safe.add_content_to_table(strip_table_key, strip_content)
        self.safe.add_content_to_table(strip_assign_table_key, strip_assign_content)

    def export_freecad_stiff_elements(self):
        fc_mpa = self.doc.Foundation.fc.getValueAs('MPa')
        self.create_concrete_material('CONCRETE_ZERO', fc_mpa, 0)
        thickness = 1500 * self.safe.length_units['mm']
        self.create_solid_slab('COL_STIFF', 'Stiff', 'CONCRETE_ZERO', thickness)
        for o in self.doc.Objects:
            if hasattr(o, "IfcType") and o.IfcType == "Column":
                z_min = o.Shape.BoundBox.ZMin
                for f in o.Shape.Faces:
                    if f.BoundBox.ZLength == 0 and f.BoundBox.ZMin == z_min:
                        points = self.get_sort_points(f.Edges)
                        self.create_area_by_coord(points, prop_name='COL_STIFF')
                        break
    
    def export_freecad_wall_loads(self):
        point_coords_table_key = "OBJECT GEOMETRY - POINT COORDINATES"
        points_content = ''
        curr_point_content = self.safe.tables_contents.get(point_coords_table_key, '')
        scale_factor = self.safe.length_units['mm']
        line_content = ''
        line_load_content = ''
        points_content = ''
        for o in self.doc.Objects:
            if (hasattr(o, "Proxy") and
                hasattr(o.Proxy, "Type") and
                o.Proxy.Type == "Wall"
                ):
                mass_per_area = o.weight
                height = o.Height.getValueAs('m')
                loadpat = o.loadpat
                value = mass_per_area * height * self.safe.force_units['Kgf'] / self.safe.length_units['m']
                p1 = o.Base.Start
                p2 = o.Base.End
                coord1 = [i * scale_factor for i in (p1.x, p1.y, p1.z)]
                coord2 = [i * scale_factor for i in (p2.x, p2.y, p2.z)]
                p1_name = self.safe.is_point_exist(coord1, curr_point_content + points_content)
                p2_name = self.safe.is_point_exist(coord2, curr_point_content + points_content)
                if p1_name is None:
                    points_content += f"Point={self.last_point_number}   GlobalX={coord1[0]}   GlobalY={coord1[1]}   GlobalZ={coord1[2]}   SpecialPt=No\n"
                    p1_name = self.last_point_number
                    self.last_point_number += 1
                if p2_name is None:
                    points_content += f"Point={self.last_point_number}   GlobalX={coord2[0]}   GlobalY={coord2[1]}   GlobalZ={coord2[2]}   SpecialPt=No\n"
                    p2_name = self.last_point_number
                    self.last_point_number += 1
                line_content += f'Line={self.last_line_number}   PointI={p1_name}   PointJ={p2_name}   LineType=Beam\n'
                name = self.last_line_number
                self.last_line_number += 1
                line_load_content += f'Line={name}   LoadPat={loadpat}   Type=Force   Dir=Gravity   DistType=RelDist   RelDistA=0   RelDistB=1   FOverLA={value}   FOverLB={value}\n'
                
        if points_content:
            self.safe.add_content_to_table(point_coords_table_key, points_content)
        table_key = "OBJECT GEOMETRY - LINES 01 - GENERAL"
        self.safe.add_content_to_table(table_key, line_content)
        table_key = "LOAD ASSIGNMENTS - LINE OBJECTS - DISTRIBUTED LOADS"
        self.safe.add_content_to_table(table_key, line_load_content)

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

    def export_punch_props(self,
            punches : Union[list, bool] = None,
            ):
        if punches is None:
            punches = []
            for o in self.doc.Objects:
                if hasattr(o, "Proxy") and \
                    hasattr(o.Proxy, "Type") and \
                    o.Proxy.Type == "Punch":
                    punches.append(o)
        punch_general_content = ''
        punch_perimeter_content = ''
        scale = self.safe.length_units['mm']
        point_coords_table_key = "OBJECT GEOMETRY - POINT COORDINATES"
        curr_point_content = self.safe.tables_contents.get(point_coords_table_key, '')
        points_coordinates = self.safe.get_points_coordinates(curr_point_content)
        scale_factor = self.safe.length_units['mm']
        for punch in punches:
            point = punch.center_of_load
            coord = [coord * scale_factor for coord in (point.x, point.y, point.z)]
            point_name = self.safe.is_point_exist(
                coordinate=coord,
                content=None,
                points_coordinates=points_coordinates,
                )
            if point_name is None:
                continue
            loc = punch.Location
            depth = punch.d * scale
            punch_general_content += f'\tPoint={point_name}   Check="Program Determined"   LocType="{loc}"   Perimeter="User Perimeter"   EffDepth=User   UserDepth={depth}   Openings=User   ReinfType=None\n'
            nulls, null_points = punch_funcs.punch_null_points(punch)
            for i, (point, is_null) in enumerate(zip(null_points, nulls), start=1):
                x, y = point.x * scale, point.y * scale
                punch_perimeter_content += f'\tPoint={point_name}   PointNum={i}   X={x}   Y={y}   Radius=0   IsNull={is_null}\n'

        punch_general_table_key = "PUNCHING SHEAR DESIGN OVERWRITES 01 - GENERAL"
        punch_perimeter_table_key = "PUNCHING SHEAR DESIGN OVERWRITES 02 - USER PERIMETER"
        self.safe.add_content_to_table(punch_general_table_key, punch_general_content)
        self.safe.add_content_to_table(punch_perimeter_table_key, punch_perimeter_content)

    def add_uniform_gravity_load(self,
        area_names : list,
        load_pat : str,
        value : float,
        ) -> None:
        table_key = "LOAD ASSIGNMENTS - SURFACE LOADS"
        content = ''
        value *= self.safe.force_units['Kgf'] / self.safe.length_units['m'] ** 2
        for area_name in area_names:
            content += f'Area={area_name}   LoadPat={load_pat}   Dir=Gravity   UnifLoad={value}   A=0   B=0   C=0\n'
        self.safe.add_content_to_table(table_key, content)

    @staticmethod
    def get_vertex_from_point(point):
        return Part.Vertex(point.x, point.y, point.z)

    def create_soil_table(self, soil_prop):
        soil_content = ''
        for name, ks in soil_prop:
            ks *= self.safe.force_units['Kgf'] / self.safe.length_units['cm'] ** 3
            soil_content += f'Soil={name}   Subgrade={ks}   NonlinOpt="Compression Only"\n'
        return soil_content

    def add_material(self,
            name : str,
            type_ : str,
            ):
        '''
        type can be 'Concrete', 'Rebar', ...
        '''
        table_key = "MATERIAL PROPERTIES 01 - GENERAL"
        material_content = f'\tMaterial={name}   Type={type_}\n'
        self.safe.add_content_to_table(table_key, material_content)
        
    def create_concrete_material(self,
            mat_name = '',
            fc_mpa = 0,
            weight = 2400,
            foun = None,
            ):
        if foun is not None:
            fc_mpa = int(foun.fc.getValueAs("MPa"))
            mat_name = f'C{fc_mpa}'
        fc = fc_mpa * self.safe.force_units['N'] / self.safe.length_units['mm'] ** 2
        self.add_material(mat_name, 'Concrete')
        table_key = "MATERIAL PROPERTIES 03 - CONCRETE"
        A = 9.9E-06
        unit_weight = weight * self.safe.force_units['Kgf'] / self.safe.length_units['m'] ** 3
        if weight == 0:
            Ec_mpa = .043 * 2400 ** 1.5 * math.sqrt(fc_mpa)
        else:
            Ec_mpa = .043 * weight ** 1.5 * math.sqrt(fc_mpa)
        Ec = Ec_mpa * self.safe.force_units['N'] / self.safe.length_units['mm'] ** 2
        mat_prop_content = f'Material={mat_name}   E={Ec}   U=0.2   A={A}   UnitWt={unit_weight}   Fc={fc}   LtWtConc=No   UserModRup=No\n'
        self.safe.add_content_to_table(table_key, mat_prop_content)
        return mat_name
    
    def create_rebar_material(self,
            mat_name = 'AIII',
            fy_mpa : int = 400,
            ):
        self.add_material(mat_name, 'Rebar')
        table_key = "MATERIAL PROPERTIES 04 - REBAR"
        weight = 7850
        unit_weight = weight * self.safe.force_units['Kgf'] / self.safe.length_units['m'] ** 3
        E = 2e5 * self.safe.force_units['N'] / self.safe.length_units['mm'] ** 2
        fy = fy_mpa * self.safe.force_units['N'] / self.safe.length_units['mm'] ** 2
        fu = 1.25 * fy
        mat_prop_content = f'Material={mat_name}   E={E}   UnitWt={unit_weight}   Fy={fy}   Fu={fu}\n'
        self.safe.add_content_to_table(table_key, mat_prop_content)
        return mat_name

    def create_solid_slab(self,
            name : str,
            type_ : str, # 'Mat', 'Stiff', 'Slab'
            material,
            thickness,
            is_thick='Yes',
            ):
        table_key = "SLAB PROPERTIES 01 - GENERAL"
        slab_general_content = f'Slab={name}   Type={type_}   ThickPlate={is_thick}\n'
        self.safe.add_content_to_table(table_key, slab_general_content)
        table_key = "SLAB PROPERTIES 02 - SOLID SLABS"
        slab_prop_content = f'Slab={name}   Type={type_}   MatProp={material}   Thickness={thickness}   Ortho=No\n'
        self.safe.add_content_to_table(table_key, slab_prop_content)

    def add_preferences(self):
        table_key = "DESIGN PREFERENCES 02 - REBAR COVER - SLABS"
        foun = self.doc.Foundation
        cover_mm = foun.cover.getValueAs('mm')
        cover = cover_mm * self.safe.length_units['mm']
        content = f'\tCoverTop={cover}   CoverBot={cover}   BarSize=18  InnerLayer=B    SlabType="Two Way"\n'
        self.safe.tables_contents[table_key] = content

def is_straight_line(edges, tol=1e-7):
    if len(edges) > 1:
        start_edge = edges[0]
        dir_start_edge = start_edge.tangentAt(start_edge.FirstParameter)
        for edge in edges:
            dir_edge = edge.tangentAt(edge.FirstParameter)
            if dir_start_edge.cross(dir_edge).Length > tol:
                return False
    return True

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
    # etabs.area.get_scale_area_points_with_scale(document.Foundation.plan_without_openings)
    SapModel = etabs.SapModel
    ret = etabs.area.export_freecad_slabs(document)
    ret = etabs.area.export_freecad_openings(openings)
    print('Wow')

