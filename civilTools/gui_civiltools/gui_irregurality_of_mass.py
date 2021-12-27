
from pathlib import Path

from PySide2 import QtCore


class CivilIrregularityOfMass:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Irregularity Of Mass")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Irregularity Of Mass")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "mass.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        data, headers = etabs.get_irregularity_of_mass()
        from civilTools import table_model
        table_model.show_results(data, headers, table_model.IrregularityOfMassModel)
        
    def IsActive(self):
        return True


        