import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

filename = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'strip.FCStd'
filename_mat = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / 'mat.FCStd'
document= FreeCAD.openDocument(str(filename))

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))

from safe_read_write_f2k import FreecadReadwriteModel as FRW

def test_export_freecad_slabs():
	document= FreeCAD.openDocument(str(filename))
	input_f2k_path = Path('~\input.f2k').expanduser()
	input_f2k_path.touch()
	output_f2k_path = Path('~\output.f2k').expanduser()
	rw = FRW(input_f2k_path, output_f2k_path, document)
	slabs, openings = rw.export_freecad_slabs()
	rw.safe.write()
	assert len(slabs) == 1
	assert len(openings) == 6

def test_export_freecad_slabs_mat():
	document= FreeCAD.openDocument(str(filename_mat))
	input_f2k_path = Path('~\input.f2k').expanduser()
	input_f2k_path.touch()
	output_f2k_path = Path('~\output_mat.f2k').expanduser()
	rw = FRW(input_f2k_path, output_f2k_path, document)
	slabs, openings = rw.export_freecad_slabs()
	rw.safe.write()
	assert len(slabs) == 5
	assert len(openings) == 0

if __name__ == '__main__':
	test_create_foundation()