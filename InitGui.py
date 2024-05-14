

class OSAFEWorkbench(Workbench):

    def __init__(self):

        from pathlib import Path
        import civilwelcome
        self.__class__.Icon = str(Path(civilwelcome.__file__).parent / 'osafe_images' / 'safe.png')
        self.__class__.MenuText = "OSAFE"
        self.__class__.ToolTip = "OSafe Workbench"

    def Initialize(self):
        from pathlib import Path
        from PySide2 import QtCore
        import OSAFEGui
        # import DraftTools

        # check user splash screen
        self.splash()
        command_list = OSAFEGui.command_list
        export_list = OSAFEGui.export_list
        draw_list = OSAFEGui.draw_list
        assign_list = OSAFEGui.assign_list
        edit_list = OSAFEGui.edit_list
        view_list = OSAFEGui.view_list
        help_list = OSAFEGui.help_list
        snap_list = OSAFEGui.snap_list

        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil tools")), command_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Export")), export_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Draw")), draw_list[:-1])
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Assign")), assign_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE Edit")), edit_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE View")), view_list[1:])
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE Snap")), snap_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil")), command_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Export")), export_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Draw")), draw_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Assign")), assign_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "OSAFE Edit")), edit_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "&View")), view_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("OSAFE", "&Help")), help_list)
        osafe_path = Path(OSAFEGui.__file__).parent
        pref_visual_ui_abs_path = str(osafe_path / 'osafe_widgets' / 'preferences-OSAFE_visual.ui')
        Gui.addPreferencePage(pref_visual_ui_abs_path, "OSAFE")
        Gui.addIconPath(str(osafe_path / "osafe_images"))
        # if int(FreeCAD.Version()[1]) > 19:
        #     # Set up Draft command lists
        #     import draftutils.init_tools as it
        #     self.draft_snap_commands = it.get_draft_snap_commands()

        #     # Set up toolbars
        #     it.init_toolbar(self,
        #                     QtCore.QT_TRANSLATE_NOOP("Workbench", "Draft snap"),
        #                     self.draft_snap_commands)

        #     # Set up preferences pages
        #     if hasattr(FreeCADGui, "draftToolBar"):
        #         if not hasattr(FreeCADGui.draftToolBar, "loadedPreferences"):
        #             FreeCADGui.addPreferencePage(":/ui/preferences-draftsnap.ui", QtCore.QT_TRANSLATE_NOOP("Draft", "Draft"))
        #             FreeCADGui.draftToolBar.loadedPreferences = True

    def Activated(self):
        import check_update
        check_update.check_updates('OSAFE')

        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetBool("show_at_startup", True):
            Gui.showPreferences("OSAFE", 0)

    def ContextMenu(self, recipient):
        if recipient == "View":
            # user clicked on the 3d view               
            # if FreeCAD.activeDraftCommand is not None:
            #     # context menu for active draft command
            #     if FreeCAD.activeDraftCommand.featureName == "Line":
            #         # BUG: "Line" gets translated, so the menu is not added correctly
            #         #      for example in italian for App.activeDraftCommand.featureName
            #         #      i get "Linea" and not "Line"
            #         #      If I correct it, the context menu display correctly, 
            #         #      but icons are grayed out, i think because we can't call them
            #         #      while another command is active. This prevents adding subcommand
            #         #      context menu entries.
            #         self.appendContextMenu("", self.lineList) # so this unuseful
            #     elif hasattr(FreeCAD.activeDraftCommand, "get_context_menu"):
            #         pass
            #         # TODO: get context menu from commands, for code i think it's more tidy
            # else:
                # context menu for selected object
            current_selection = FreeCADGui.Selection.getSelection()
            if len(current_selection) == 1:
                obj = current_selection[0]
                if hasattr(obj, 'IfcType') and obj.IfcType == 'Footing':
                # TODO: Current implementation add lots of commands to the context
                #       menu. I think we ca simplify it and add some separators
                #       to keep everything more tidy.
                #       Also the command could get context menu from the object view
                #       provider since it already have one setupContextMenu method.
                    self.appendContextMenu('', ['osafe_explode_foundation'])
        # else:
        #     # user clicked somewhere else on the Gui 
        #     # TODO: i think we can discard this usecase, since the threeview
        #     #       has already it's context menu entries in the viewprovider
        #     if FreeCADGui.Selection.getSelection():
        #         self.appendContextMenu("Utilities", self.treecmdList)

    def splash(self):
        from pathlib import Path
        import shutil
        # param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
        # image = Path(param.GetString('splash_screen'))
        user_path = Path(FreeCAD.getUserAppDataDir())   
        # if not image.exists():
        image = user_path / 'Mod' / 'OSAFE' / 'osafe_images' / 'civiltools.png'
        if not image.exists():
            return
        splash_path = (user_path / 'Gui' / 'images')
        try:
            splash_path.mkdir(parents=True)
        except FileExistsError:
            pass
        suffix = image.suffix
        splash_image_path = splash_path / f'splash_image{suffix}'
        # check if splash image folder is empty
        hash_md5 = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").GetString("splash_hash_md5", '')
        splash_hash_md5 = "85b13cbcb16dca64d61456f56d54e4d3"
        if hash_md5 != splash_hash_md5:
            for i in splash_path.glob("splash_image.*"):
                i.unlink()
            shutil.copy(image, splash_image_path)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetString("splash_hash_md5", splash_hash_md5)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").SetString("splash_hash_md5", splash_hash_md5)
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
