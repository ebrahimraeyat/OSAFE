import sys
from pathlib import Path


# path to FreeCAD
FREECADPATH = r'G:\Program Files\FreeCAD 0.21\bin'
sys.path.append(FREECADPATH)
import FreeCAD

osafe_path = Path(__file__).absolute().parent.parent.parent
sys.path.insert(0, str(osafe_path))
from osafe_export import to_xc


filename = osafe_path / 'test' / 'files' / 'foun.FCStd'
foun_document= FreeCAD.openDocument(str(filename))

def get_temp_file_path(filename=''):
    import tempfile
    default_tmp_dir = tempfile._get_default_tempdir()
    if not filename:
        filename = 'test.py'
    return Path(default_tmp_dir) / filename

def test_get_columns_points():
    file_path = get_temp_file_path()
    writer = to_xc.FreecadReadwriteModel(file_path, foun_document)
    writer.add_program_control()
    writer.add_import_statements()
    writer.add_columns_points()
    writer.add_graphic_stuff()
    writer.write()

def test_add_area_by_coord():
    file_path = get_temp_file_path()
    writer = to_xc.FreecadReadwriteModel(file_path, foun_document)
    p1 = FreeCAD.Vector(0, 0, 0)
    p2 = FreeCAD.Vector(1, 0, 0)
    p3 = FreeCAD.Vector(1, 1, 0)
    p4 = FreeCAD.Vector(0, 1, 0)
    points = [p1, p2, p3, p4]
    writer.add_area_by_coord(points)
    writer.write()

def test_add_slabs():
    file_path = get_temp_file_path(filename='mesh.py')
    writer = to_xc.FreecadReadwriteModel(file_path, foun_document)
    writer.add_program_control()
    writer.add_import_statements()
    writer.add_columns_points()
    slabs = writer.add_slabs()
    writer.add_mesh_generation(slabs)
    writer.add_graphic_stuff()
    writer.write()

def test_add_soil_support():
    file_path = get_temp_file_path(filename='soil.py')
    writer = to_xc.FreecadReadwriteModel(file_path, foun_document)
    writer.add_program_control()
    writer.add_import_statements()
    writer.add_columns_points()
    slabs = writer.add_slabs()
    writer.add_mesh_generation(slabs)
    writer.add_soil_support(slabs, 2)
    writer.add_graphic_stuff()
    writer.write()
