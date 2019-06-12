import civilGui


class CivilWorkbench(Workbench):

    def __init__(self):
        rel_path = "Mod/Civil/images/civil-engineering.png"
        icon_path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(icon_path):
            icon_path = FreeCAD.ConfigGet("UserAppData") + rel_path

        self.__class__.Icon = icon_path
        self.__class__.MenuText = "Civil"
        self.__class__.ToolTip = "Civil Workbench"

    def Initialize(self):
        from PySide2 import QtCore, QtGui
        command_list = ["Punch"]

        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Civil tools")), command_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Civil")), command_list)


Gui.addWorkbench(CivilWorkbench())
