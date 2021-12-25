
from pathlib import Path

import PySide2
from PySide2 import QtCore

import FreeCAD
import FreeCADGui as Gui



class CivilSettings:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Settings")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Setting for cfactor")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "settings.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        def get_mdiarea():
            """ Return FreeCAD MdiArea. """
            mw = Gui.getMainWindow()
            if not mw:
                return None
            childs = mw.children()
            for c in childs:
                if isinstance(c, PySide2.QtWidgets.QMdiArea):
                    return c
            return None

        mdi = get_mdiarea()
        if not mdi:
            return None
        self.initiate()
        from civilTools import civiltools
        self.win = civiltools.Ui()
        sub = mdi.addSubWindow(self.win)
        sub.show()
        
    def IsActive(self):
        return True

    def initiate(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = App.newDocument()
        if not hasattr(doc, 'Site'):
            import Arch
            site = Arch.makeSite([])
            build = Arch.makeBuilding([])
            # build.recompute()
            site.Group = [build]
            doc.recompute()

        