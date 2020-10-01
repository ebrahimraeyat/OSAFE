import FreeCAD
import os


class CivilWorkbench(Workbench):

    def __init__(self):
        rel_path = "Mod/Civil/images/civil-engineering.png"
        pref_visual_ui_rel_path = "Mod/Civil/ui/preferences-punch_visual.ui"
        self.pref_visual_ui_abs_path = FreeCAD.ConfigGet("AppHomePath") + pref_visual_ui_rel_path
        import os
        if not os.path.exists(self.pref_visual_ui_abs_path):
            self.pref_visual_ui_abs_path = FreeCAD.ConfigGet("UserAppData") + pref_visual_ui_rel_path

        icon_path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        if not os.path.exists(icon_path):
            icon_path = FreeCAD.ConfigGet("UserAppData") + rel_path

        self.__class__.Icon = icon_path
        self.__class__.MenuText = "Civil"
        self.__class__.ToolTip = "Civil Workbench"

    def Initialize(self):
        from PySide2 import QtCore, QtGui
        import civilGui
        from pathlib import Path

        command_list = civilGui.command_list

        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Civil tools")), command_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Civil")), command_list)
        Gui.addPreferencePage(self.pref_visual_ui_abs_path, "punch")
        Gui.addIconPath(
            str(
                Path(civilGui.__file__).parent.absolute()
                / "images"
                )
            )

    def Activated(self):
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("FirstTime", True):
            from DraftGui import todo
            todo.delay(FreeCADGui.runCommand, "Civil_welcome")


Gui.addWorkbench(CivilWorkbench())
