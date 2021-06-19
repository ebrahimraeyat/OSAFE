import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# path to FreeCAD.so
FREECADPATH = '/usr/lib/freecad-daily-python3/lib/'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import report

import pandas as pd
import docx

filename = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / '1.FCStd'
document= FreeCAD.openDocument(str(filename))

def test_get_punch_picture():
	punch = document.Punch
	fname = report.get_punch_picture(punch, 'jafari')
	assert True
	assert str(fname) == '/tmp/jafari.jpg'

def test_add_punch_edges_to_ax():
	punch = document.Punch
	fig = plt.figure()
	ax1 = fig.add_subplot(211, aspect='equal')
	plt.axis('off')
	report.add_punch_edges_to_ax(punch, ax1)
	fig.savefig('/tmp/jafari1.jpg')

def test_export_dataframe_to_docx():
	punch = document.Punch
	df = pd.DataFrame(list(punch.combos_ratio.items()), columns=['Combo', 'Ratio'])
	doc = report.export_dataframe_to_docx(df)
	doc.save('/home/ebi/alaki/jafari.docx')

def test_create_report():
	punch = document.Punch
	filename = '/home/ebi/alaki/jafari.docx'
	report.create_report(punch, filename)

test_get_punch_picture()
test_create_report()