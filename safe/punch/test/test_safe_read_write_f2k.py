import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD
import pytest

filename = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'strip.FCStd'
filename_mat = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'mat.FCStd'
filename_kazemi = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'kazemi.FCStd'
document= FreeCAD.openDocument(str(filename))
document_mat= FreeCAD.openDocument(str(filename_mat))
document_kazemi= FreeCAD.openDocument(str(filename_kazemi))

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))

from safe_read_write_f2k import FreecadReadwriteModel as FRW
from safe_read_write_f2k import Safe, Safe12

def test_export_freecad_slabs():
    rw = FRW(doc=document_kazemi)
    slabs = rw.export_freecad_slabs()
    rw.safe.write()
    assert len(slabs) == 33

def test_export_freecad_wall_loads():
    input_f2k_path = Path('~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path('~\\wall_loads.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    rw.export_freecad_wall_loads()
    rw.safe.write()

def test_add_uniform_gravity_load():
    input_f2k_path = Path('~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path('~\\uniform.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    slabs = rw.export_freecad_slabs()
    rw.add_uniform_gravity_load(slabs, 'DEAD', 200)
    rw.safe.write()
    assert len(slabs) == 1
    # Mat 
    output_f2k_path = Path('~\\uniform_mat.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document_mat)
    slabs = rw.export_freecad_slabs()
    rw.add_uniform_gravity_load(slabs, 'DEAD', 200)
    rw.safe.write()
    assert len(slabs) == 5


def test_export_freecad_slabs_mat():
    input_f2k_path = Path('~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path('~\output_mat.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document_mat)
    slabs = rw.export_freecad_slabs()
    rw.safe.write()
    assert len(slabs) == 5

def test_export_freecad_openings():
    input_f2k_path = Path('~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path('~\output_mat.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document_mat)
    slabs = rw.export_freecad_openings()
    rw.safe.write()
    assert len(slabs) == 1

def test_export_freecad_strips():
    rw = FRW(doc=document_kazemi)
    rw.export_freecad_strips()
    rw.safe.write()

def test_export_freecad_mat_strips():
    rw = FRW(doc=document)
    rw.export_freecad_strips()
    rw.safe.write()

def test_add_preferences():
    input_f2k_path = Path('~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path('~\pref.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    rw.add_preferences()
    rw.safe.write()

def test_export_freecad_stiff_elements():
    rw = FRW(doc=document_kazemi)
    rw.export_freecad_stiff_elements()
    rw.safe.write()

def test_export_punch_props():
    input_f2k_path = Path('~\input.f2k').expanduser()
    input_f2k_path.touch()
    output_f2k_path = Path('~\punch.f2k').expanduser()
    rw = FRW(input_f2k_path, output_f2k_path, document)
    rw.export_punch_props()
    rw.safe.write()

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
                Point=121   GlobalX=17690   GlobalY=0   GlobalZ=0   SpecialPt=Yes\n'''

    id = safe.is_point_exist([2820, 0, 0], content)
    assert id == '115'
    id = safe.is_point_exist([2820, 20, 0], content)
    assert not id

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

if __name__ == '__main__':
    test_export_freecad_mat_strips()