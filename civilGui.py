import PySide2
from PySide2 import QtCore, QtGui
import FreeCAD
import FreeCADGui as Gui
import os
from safe.punch import punchPanel


class Punch:
    def Activated(self):
        panel = punchPanel.PunchTaskPanel()
        Gui.Control.showDialog(panel)
        if panel.setupUi():
            Gui.Control.closeDialog(panel)
            return None
        return panel

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Punch",
            "control Punch")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Punch",
            "control shear punching")
        return {'Pixmap': FreeCAD.ConfigGet("AppHomePath") + "Mod/Civil/images/punch.svg",
                'MenuText': MenuText,
                'ToolTip': ToolTip}


Gui.addCommand('Punch', Punch())
