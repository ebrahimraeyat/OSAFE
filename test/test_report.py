import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# path to FreeCAD
# FREECADPATH = '/usr/lib/freecad-daily-python3/lib/'
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(punch_path))
import report

import pandas as pd

filename = Path(__file__).absolute().parent.parent / 'test_files' / 'freecad' / '2.FCStd'
document= FreeCAD.openDocument(str(filename))

def test_get_punch_picture():
    punch = document.Punch004
    fname = report.get_punch_picture(punch)
    assert True
    assert str(fname) == '/tmp/Punch.jpg'

def test_add_punch_edges_to_ax():
    punch = document.Punch004
    fig = plt.figure()
    ax1 = fig.add_subplot(211, aspect='equal')
    plt.axis('off')
    report.add_punch_edges_to_ax(punch, ax1)
    fig.savefig('/tmp/jafari1.jpg')

def test_export_dataframe_to_docx():
    punch = document.Punch004
    df = pd.DataFrame(list(punch.combos_ratio.items()), columns=['Combo', 'Ratio'])
    doc = report.export_dataframe_to_docx(df)
    doc.save('c:\\alaki\\jafari.docx')

def test_create_report():
    punch = document.Punch004
    filename = 'c:\\alaki\\jafari.docx'
    report.create_report(punch, filename)

def test_get_edges_direction_in_punch():
    punch = document.Punch004
    edges_direction = report.get_edges_direction_in_punch(punch)
    assert list(edges_direction.values()) == ['BOT', 'RIGHT', 'TOP']

def test_export_dict_to_doc():
    d = {'location': 'center', 'id': 227}
    doc = report.export_dict_to_doc(d, [])
    doc.save('c:\\alaki\\jafari.docx')
    assert True

def test_add_punch_properties_to_doc():
    punch = document.Punch004
    doc = report.add_punch_properties_to_doc(punch)
    doc.save('c:\\alaki\\jafari.docx')
    assert True

def test_create_punches_report():
    report.create_punches_report(document, 'c:\\alaki\\jafari.docx')

# test_get_punch_picture()
test_create_report()
# test_add_punch_properties_to_doc()
# test_export_dict_to_doc()
# test_create_punches_report()