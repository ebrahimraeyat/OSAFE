import sys
from pathlib import Path

import matplotlib.pyplot as plt

# path to FreeCAD
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

punch_path = Path(__file__).parent.parent.parent
etabs_api_path = punch_path.parent / 'etabs_api'
sys.path.insert(0, str(punch_path))
sys.path.insert(1, str(etabs_api_path))
from osafe_import_export import report

from python_functions import get_temp_filepath
from freecad_funcs import open_file


import pandas as pd

filename = punch_path / 'test' / 'test_files' / 'freecad' / 'base_plate.FCStd'
document= FreeCAD.openDocument(str(filename))

def test_get_punch_picture():
    punch = document.Punch
    filename = get_temp_filepath(suffix='jpg', filename='test')
    fname = report.get_punch_picture(punch, filename=filename)
    assert fname.exists()
    open_file(fname)

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
    doc.save('c:\\alaki\\jafari.docx')

def test_create_report():
    punch = document.Punch
    filename = 'c:\\alaki\\jafari.docx'
    report.create_report(punch, filename)

def test_get_edges_direction_in_punch():
    punch = document.Punch
    edges_direction = report.get_edges_direction_in_punch(punch)
    assert list(edges_direction.values()) == ['BOT', 'RIGHT', 'TOP']

def test_export_dict_to_doc():
    d = {'location': 'center', 'id': 227}
    doc = report.export_dict_to_doc(d, [])
    doc.save('c:\\alaki\\jafari.docx')
    assert True

def test_add_punch_properties_to_doc():
    punch = document.Punch
    doc = report.add_punch_properties_to_doc(punch)
    doc.save('c:\\alaki\\jafari.docx')
    assert True

def test_create_punches_report():
    report.create_punches_report(document, 'c:\\alaki\\jafari.docx')


if __name__ == '__main__':
    # test_get_punch_picture()
    test_create_report()
    # test_add_punch_properties_to_doc()
    # test_export_dict_to_doc()
    # test_create_punches_report()