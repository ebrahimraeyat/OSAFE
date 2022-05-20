import FreeCAD

FreeCAD.addImportType("CSI SAFE (*.xls *.xlsx)", "safe.punch.geom")
FreeCAD.addImportType("CSI ETABS (*.edb *.EDB)", "safe.punch.open_etabs")
