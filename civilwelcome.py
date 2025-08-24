import os
import FreeCAD
import FreeCADGui

from PySide import QtCore, QtGui


def QT_TRANSLATE_NOOP(ctx, txt): return txt


class CivilWelcome:

    def GetResources(self):
        return {'Pixmap': os.path.join(os.path.dirname(__file__), "Images", "civil_welcom.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Civil_welcome", "Civil welcome screen"),
                'ToolTip': QT_TRANSLATE_NOOP("Civil_welcome", "Show the Civil workbench welcome screen")}

    def Activated(self):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__), "ui", "civil_welcome.ui"))
        self.form.image.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "images", "banner.jpg")))

        result = self.form.exec_()
        # if result:
        #     FreeCADGui.runCommand("Civil_Setup")

        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetBool("FirstTime", False)
