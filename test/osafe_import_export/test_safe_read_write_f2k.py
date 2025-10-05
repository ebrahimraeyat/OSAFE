import sys
from pathlib import Path
import tempfile
import re

# path to FreeCAD.so
FREECADPATH = str(Path(sys.executable).parent)
sys.path.append(FREECADPATH)
import FreeCAD
import pytest

temp_dir = tempfile.gettempdir()
output_f2k_path = Path(temp_dir) / 'output.f2k'

filename_rashidzadeh = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'rashidzadeh.FCStd'
filename_single_foundation = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'single_foundation.FCStd'
input_f2k = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'khalaji.F2k'

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))

from osafe_import_export.safe_read_write_f2k import FreecadReadwriteModel as FRW
from osafe_import_export.safe_read_write_f2k import Safe, Safe12
import osafe_funcs.osafe_funcs as osf


def test_export_freecad_slabs():
    rw = FRW(doc=document_kazemi)
    slabs = rw.export_freecad_slabs()
    rw.safe.write()
    assert len(slabs) == 33


def test_export_freecad_single_slabs():
    doc_single_foundation = FreeCAD.openDocument(str(filename_single_foundation))
    rw = FRW(output_f2k_path=output_f2k_path, doc=doc_single_foundation)
    slabs = rw.export_freecad_single_slabs()
    rw.safe.write()
    assert Path(output_f2k_path).exists()

    # Expected points and coordinates
    expected_points = {
        172: (35967.63671875, 16168.472656250004, 0.0),
        173: (35967.63671875, 24168.472656250004, 0.0),
        174: (27967.63671875, 24168.472656250004, 0.0),
        175: (27967.63671875, 16168.472656250004, 0.0),
        176: (41320.33203125, 5629.059570312502, 0.0),
        177: (41320.33203125, 13629.059570312502, 0.0),
        178: (33320.33203125, 13629.059570312502, 0.0),
        179: (33320.33203125, 5629.059570312502, 0.0),
    }
    expected_areas = {
        1000: [172, 173, 174, 175],
        1001: [176, 177, 178, 179],
    }

    with open(output_f2k_path, 'r') as f:
        content = f.read()

    # Check points
    for pt_num, coords in expected_points.items():
        found = False
        for line in content.splitlines():
            if f"Point={pt_num}" in line:
                # Extract coordinates from line
                try:
                    gx = float(line.split("GlobalX=")[1].split()[0])
                    gy = float(line.split("GlobalY=")[1].split()[0])
                    gz = float(line.split("GlobalZ=")[1].split()[0])
                    # Compare with expected (allow small tolerance)
                    if (abs(gx - coords[0]) < 1e-6 and
                        abs(gy - coords[1]) < 1e-6 and
                        abs(gz - coords[2]) < 1e-6):
                        found = True
                        break
                except Exception:
                    continue
        assert found, f"Point {pt_num} with correct coordinates not found in output file"

def test_export_freecad_single_slabs_all():
    doc_single_foundation = FreeCAD.openDocument(str(filename_single_foundation))
    rw = FRW(output_f2k_path=output_f2k_path, doc=doc_single_foundation)
    rw.export_freecad_slabs()
    rw.export_freecad_single_slabs()
    rw.safe.write()
    assert Path(output_f2k_path).exists()
    # Expected points and coordinates
    expected_coords = [
        (35967.63671875, 16168.472656250004, 0.0),
        (35967.63671875, 24168.472656250004, 0.0),
        (27967.63671875, 24168.472656250004, 0.0),
        (27967.63671875, 16168.472656250004, 0.0),
        (41320.33203125, 5629.059570312502, 0.0),
        (41320.33203125, 13629.059570312502, 0.0),
        (33320.33203125, 13629.059570312502, 0.0),
        (33320.33203125, 5629.059570312502, 0.0),
    ]
    expected_areas = [
        [0, 1, 2, 3],  # indices in expected_coords for area 1
        [4, 5, 6, 7],  # indices in expected_coords for area 2
    ]

    with open(output_f2k_path, 'r') as f:
        content = f.read()

    # 1. Find all points and their coordinates
    point_pattern = re.compile(r'Point=(\d+)\s+GlobalX=([0-9eE\.\-]+)\s+GlobalY=([0-9eE\.\-]+)\s+GlobalZ=([0-9eE\.\-]+)')
    points = {}
    for match in point_pattern.finditer(content):
        num = int(match.group(1))
        x = float(match.group(2))
        y = float(match.group(3))
        z = float(match.group(4))
        points[num] = (x, y, z)

    # 2. For each expected coordinate, find the matching point number
    def find_point_number(coord):
        for num, pt in points.items():
            if all(abs(a-b) < 1e-4 for a, b in zip(coord, pt)):
                return num
        return None

    found_point_numbers = [find_point_number(coord) for coord in expected_coords]
    assert all(pn is not None for pn in found_point_numbers), "Not all expected points found in file"

    # 3. Find all areas and their point references
    area_pattern = re.compile(r'Area=(\d+).*?Point1=(\d+).*?Point2=(\d+).*?Point3=(\d+).*?Point4=(\d+)', re.DOTALL)
    areas = []
    for match in area_pattern.finditer(content):
        area_num = int(match.group(1))
        pts = [int(match.group(i)) for i in range(2, 6)]
        areas.append((area_num, pts))

    # 4. For each expected area, check if any area uses the found point numbers
    for area_indices in expected_areas:
        expected_pts = [found_point_numbers[i] for i in area_indices]
        found = any(all(pt in area_pts for pt in expected_pts) for _, area_pts in areas)
        assert found, f"Area with points {expected_pts} not found in file"


def test_export_freecad_wall_loads():
    input_f2k_path = Path(r'~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path(r'~\wall_loads.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    rw.export_freecad_wall_loads()
    rw.safe.write()

def test_add_uniform_gravity_load():
    input_f2k_path = Path(r'~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path(r'~\uniform.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    slabs = rw.export_freecad_slabs()
    rw.add_uniform_gravity_load(slabs, 'DEAD', 200)
    rw.safe.write()
    assert len(slabs) == 1
    # Mat 
    output_f2k_path = Path(r'~\uniform_mat.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document_mat)
    slabs = rw.export_freecad_slabs()
    rw.add_uniform_gravity_load(slabs, 'DEAD', 200)
    rw.safe.write()
    assert len(slabs) == 5


def test_export_freecad_slabs_mat():
    input_f2k_path = Path(r'~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path(r'~\output_mat.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document_mat)
    slabs = rw.export_freecad_slabs()
    rw.safe.write()
    assert len(slabs) == 5

def test_export_freecad_openings():
    input_f2k_path = Path(r'~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path(r'~\output_mat.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document_mat)
    slabs = rw.export_freecad_openings()
    rw.safe.write()
    assert len(slabs) == 1

def test_export_freecad_strips():
    document = FreeCAD.openDocument(str(filename_rashidzadeh))
    rw = FRW(doc=document)
    rw.export_freecad_strips()
    rw.safe.write()
    strips = osf.get_objects_of_type("Strip")
    for strip in strips:
        osf.remove_obj(strip.Name)
    rw.export_freecad_strips()
    rw.safe.write()

def test_export_freecad_mat_strips():
    rw = FRW(doc=document)
    rw.export_freecad_strips()
    rw.safe.write()

def test_add_preferences():
    input_f2k_path = Path(r'~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path(r'~\pref.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    rw.add_preferences()
    rw.safe.write()

def test_export_freecad_stiff_elements():
    rw = FRW(doc=document_kazemi)
    rw.export_freecad_stiff_elements()
    rw.safe.write()

def test_export_punch_props():
    output_f2k_path = Path(r'~\punch.f2k').expanduser()
    rw = FRW(input_f2k, output_f2k_path, document_khalaji)
    rw.export_punch_props()
    rw.safe.write()
    with open(output_f2k_path, 'r') as f:
        for line in f:
            if "IsNull=No" in line:
                assert True
                return
    assert False

def test_export_freecad_columns():
    output_f2k_path = Path(r'~\columns.f2k').expanduser()
    doc = FreeCAD.openDocument(str(filename_adampira))
    rw = FRW(input_f2k, output_f2k_path, doc)
    rw.export_freecad_columns()
    rw.safe.write()
    obj_geo_line01 = False
    col_prop_general = False
    col_prop_rec = False
    col_prop_assign = False
    col_prop_mod = False
    col_prop_angle = False
    col_prop_insertion = False
    with open(output_f2k_path, 'r') as f:
        for line in f:
            if "Line=1008   PointI=51   PointJ=52   LineType=Column" in line:
                obj_geo_line01 = True
            if "Column=COL1008   Type=Rectangular" in line:
                col_prop_general = True
            if "Column=COL1007   MatProp=CONCRETE_ZERO   SecDim2=700.0   SecDim3=500.0" in line:
                col_prop_rec = True
            if "Line=1006 ColProp=COL1006" in line:
                col_prop_assign = True
            if "Line=1008   Area=1   As2=1   As3=1   J=1   I22=0.7   I33=0.7   Weight=1" in line:
                col_prop_mod = True
            if "Line=1004 Angle=50." in line:
                col_prop_angle = True
            if 'Line=1006   CardinalPt="10 (centroid)"' in line:
                col_prop_insertion = True
    for col_prop in (
        obj_geo_line01,
        col_prop_general,
        col_prop_rec,
        col_prop_assign,
        col_prop_mod,
        col_prop_angle,
        col_prop_insertion,
    ):
        assert col_prop
            
def test_get_points_coordinates():
    safe = Safe()
    content = '''Point=115   GlobalX=2820   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=117   GlobalX=7040   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n   
                Point=119   GlobalX=14690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=121   GlobalX=17690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n'''

    points_coordinates = safe.get_points_coordinates(content)
    assert set(points_coordinates.keys()) == set(['115', '117', '119', '121'])
    assert points_coordinates['115'] == [2820, 0, 0]

def test_is_point_exist():
    safe = Safe()
    content = '''Point=115   GlobalX=2820   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=117   GlobalX=7040   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n   
                Point=119   GlobalX=14690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=121   GlobalX=17690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=122   GlobalX=1   GlobalY=8969.629120788806   GlobalZ=0   SpecialPt=Yes\n
                Point=123   GlobalX=0   GlobalY=8900   GlobalZ=0   SpecialPt=Yes\n
                '''

    id = safe.is_point_exist([2820, 0, 0], content)
    assert id == '115'
    # float coordinate
    id = safe.is_point_exist([2820.0001, 0, 0], content)
    assert id == '115'
    id = safe.is_point_exist([2820, 20, 0], content)
    assert not id
    id = safe.is_point_exist([1, 8900, 0], content)
    assert not id

def test_get_last_point_number():
    safe = Safe()
    content = '''Point=115   GlobalX=2820   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=119   GlobalX=14690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=123   GlobalX=0   GlobalY=8900   GlobalZ=0   SpecialPt=Yes\n
                Point=121   GlobalX=17690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n
                Point=122   GlobalX=1   GlobalY=8969.629120788806   GlobalZ=0   SpecialPt=Yes\n
                Point=117   GlobalX=7040   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n   
                '''

    id_ = safe.get_last_point_number(content)
    assert id_ == 124
    content += "Point=~200   GlobalX=7045   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n"   
    id_ = safe.get_last_point_number(content)
    assert id_ == 124
    id_ = safe.get_last_point_number(content='1')
    assert id_ == 1000000

def test_set_sthtbelow():
    safe = Safe()
    content16 = 'ProgramName="SAFE 2016"   Version=16.0.2   ProgLevel="Post Tensioning"   LicenseNum=*1ZAU45DLGK2A3EX   CurrUnits="Kgf, m, C"   MergeTol=0.0025   ModelDatum=0   StHtAbove=0   StHtBelow=3000   ConcCode="ACI 318-14"'
    safe.force_length_unit(content16)
    content = safe.set_sthtbelow(content=content16)
    assert content == content16.replace('3000', '0')
    # version 14
    content14 = 'ProgramName="SAFE 2014"   Version=14.0.0   ProgLevel="Post Tensioning"   CurrUnits="N, mm, C"  ModelDatum=0.0'
    safe.force_length_unit(content14)
    content = safe.set_sthtbelow(content=content14)
    assert content == content14[:-2]

def test_force_length_unit():
    safe = Safe()
    content = 'ProgramName="SAFE 2016"   Version=16.0.2   ProgLevel="Post Tensioning"   LicenseNum=*1ZAU45DLGK2A3EX   CurrUnits="Kgf, m, C"   MergeTol=0.0025   ModelDatum=0   StHtAbove=0   StHtBelow=3000   ConcCode="ACI 318-14"'
    safe.force_length_unit(content)
    assert safe.force_unit == 'Kgf'
    assert safe.length_unit == 'm'
    # soil ks 2 kgf / cm3 -> kgf / m3
    ks = 2 * safe.force_units['Kgf'] / safe.length_units['cm'] ** 3
    assert pytest.approx(ks, 2e6, abs=.01)
    
    content = 'ProgramName="SAFE 2016"   Version=16.0.2   ProgLevel="Post Tensioning"   LicenseNum=*1ZAU45DLGK2A3EX   CurrUnits="Kgf, mm, C"   MergeTol=0.0025   ModelDatum=0   StHtAbove=0   StHtBelow=3000   ConcCode="ACI 318-14"'
    safe.force_length_unit(content)
    assert safe.force_unit == 'Kgf'
    assert safe.length_unit == 'mm'
    # soil ks 2 kgf / cm3 -> kgf / mm3
    ks = 2 * safe.force_units['Kgf'] / safe.length_units['cm'] ** 3
    assert pytest.approx(ks, 2e-3, abs=.0001)
    
    content = 'ProgramName="SAFE 2016"   Version=16.0.2   ProgLevel="Post Tensioning"   LicenseNum=*1ZAU45DLGK2A3EX   CurrUnits="kN, mm, C"   MergeTol=0.0025   ModelDatum=0   StHtAbove=0   StHtBelow=3000   ConcCode="ACI 318-14"'
    safe.force_length_unit(content)
    assert safe.force_unit == 'kN'
    assert safe.length_unit == 'mm'
    # soil ks 2 kgf / cm3 -> kN / mm3
    ks = 2 * safe.force_units['Kgf'] / safe.length_units['cm'] ** 3
    assert pytest.approx(ks, 1.9613e-05, .01)


def test_get_points_coordinates12():
    safe = Safe12()
    content = '''  POINT  "115"  2.82  0\n
                    POINT  "117"  7.04  0\n
                    POINT  "119"  14.69  0\n
                    POINT  "121"  17.69  0'''

    points_coordinates = safe.get_points_coordinates(content)
    assert set(points_coordinates.keys()) == set(['115', '117', '119', '121'])
    assert points_coordinates['115'] == [2.82, 0]

def test_is_point_exist12():
    safe = Safe12()
    content = '''  POINT  "115"  2.82  0\n
                    POINT  "117"  7.04  0\n
                    POINT  "119"  14.69  0\n
                    POINT  "121"  17.69  0'''
    id = safe.is_point_exist([2.82, 0], content)
    assert id == '115'
    id = safe.is_point_exist([2.820, .20], content)
    assert not id

def test_get_f2k_version():
    from safe_read_write_f2k import get_f2k_version
    # version 14, 16
    content = 'ProgramName="SAFE 2016"   Version=%i.0.2   ProgLevel="Post Tensioning"   LicenseNum=*1ZAU45DLGK2A3EX   CurrUnits="Kgf, m, C"   MergeTol=0.0025   ModelDatum=0   StHtAbove=0   StHtBelow=3000   ConcCode="ACI 318-14"'
    for version in (14, 16):
        ver = get_f2k_version(doc='alaki', content=content % version)
        assert version == ver
    ver = get_f2k_version(doc='alaki', content=content % 200)
    assert ver is None
    # version 8, 12
    content = r'''$ File G:\design\97\hajrezaee\mosavab\etabs\hajrezaee_97-03-01.e2k saved 5/26/2016 5:10:58 AM
 
                SAFE %s.2.0.S
                UNITS  kgf  m
                $ TITLES'
            '''
    ver = get_f2k_version(doc='alaki', content=content % '12')
    assert ver == 12
    ver = get_f2k_version(doc='alaki', content=content % '"8')
    assert ver == 8
    ver = get_f2k_version(doc='alaki', content=content % '8')
    assert ver is None

if __name__ == '__main__':
    test_export_freecad_single_slabs()