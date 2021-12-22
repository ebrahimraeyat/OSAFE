
from pathlib import Path

# import PySide2
from PySide2 import QtCore


# import FreeCAD
import FreeCADGui as Gui



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
        # def get_mdiarea():
        #     """ Return FreeCAD MdiArea. """
        #     mw = Gui.getMainWindow()
        #     if not mw:
        #         return None
        #     childs = mw.children()
        #     for c in childs:
        #         if isinstance(c, PySide2.QtWidgets.QMdiArea):
        #             return c
        #     return None

        # mdi = get_mdiarea()
        # if not mdi:
        #     return None
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        data, headers = etabs.get_irregularity_of_mass()
        table_model.show_results(data, headers, table_model.IrregularityOfMassModel)
        
    def IsActive(self):
        return True


        