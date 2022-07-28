

class OSAFEWorkbench(Workbench):

    def __init__(self):

        from pathlib import Path
        import civilwelcome
        self.__class__.Icon = str(Path(civilwelcome.__file__).parent.absolute() / 'images' / 'safe.png')
        self.__class__.MenuText = "OSAFE"
        self.__class__.ToolTip = "OSafe Workbench"

    def Initialize(self):
        from pathlib import Path
        from PySide2 import QtCore
        import OSAFEGui

        # check user splash screen
        self.splash()
        command_list = OSAFEGui.command_list
        export_list = OSAFEGui.export_list
        draw_list = OSAFEGui.draw_list
        assign_list = OSAFEGui.assign_list
        edit_list = OSAFEGui.edit_list
        view_list = OSAFEGui.view_list

        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil tools")), command_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Export")), export_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Draw")), draw_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Assign")), assign_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE Edit")), edit_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE View")), view_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil")), command_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Export")), export_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Draw")), draw_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Assign")), assign_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE Edit")), edit_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "&View")), view_list)

        pref_visual_ui_abs_path = str(Path(OSAFEGui.__file__).parent.absolute() / 'ui' / 'preferences-OSAFE_visual.ui')
        Gui.addPreferencePage(pref_visual_ui_abs_path, "OSAFE")
        Gui.addIconPath(
            str(
                Path(OSAFEGui.__file__).parent.absolute()
                / "images"
                )
            )

    def Activated(self):
        from DraftGui import todo
        import check_update
        todo.delay(check_update.check_updates, 'OSAFE')

        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetBool("show_at_startup", True):
            Gui.showPreferences("OSAFE", 0)
        FreeCAD.addImportType("CSI ETABS (*.edb *.EDB)", "safe.punch.open_etabs")

    def splash(self):
        from pathlib import Path
        import shutil
        # param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
        # image = Path(param.GetString('splash_screen'))
        user_path = Path(FreeCAD.getUserAppDataDir())   
        # if not image.exists():
        image = user_path / 'Mod' / 'OSAFE' / 'images' / 'splash.png'
        if not image.exists():
            return
        splash_path = (user_path / 'Gui' / 'images')
        try:
            splash_path.mkdir(parents=True)
        except FileExistsError:
            pass
        suffix = image.suffix
        splash_image_path = splash_path / f'splash_image{suffix}'
        splashes = [i for i in splash_path.glob("splash_image.*")]
        # check if splash image folder is empty
        if not splashes:
            shutil.copy(image, splash_image_path)
            return
        # import hashlib
        # image_md5 = hashlib.md5(open(image, 'rb').read()).hexdigest()
        # exists = False
        # for si_path in splashes:
        #     splash_md5 =  hashlib.md5(open(si_path, 'rb').read()).hexdigest()
        #     if image_md5 == splash_md5:
        #         exists = True
        #     else:
        #         si_path.unlink()
        # if not exists:
        #     shutil.copy(image, splash_image_path)

Gui.addWorkbench(OSAFEWorkbench())
