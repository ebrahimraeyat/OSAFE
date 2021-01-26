import os
from pathlib import Path
import PySide2
from PySide2 import QtCore, QtGui
import FreeCAD
import FreeCADGui as Gui
import DraftTools
import civilwelcome

def QT_TRANSLATE_NOOP(ctx, txt): return txt


class Copy(DraftTools.Move):

    def __init__(self):
        DraftTools.Move.__init__(self)

    def GetResources(self):

        return {'Pixmap': os.path.join(os.path.dirname(__file__), "images", "copy.svg"),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Copy", "Copy"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("TogglePanels", "Copies selected objects to another location"),
                'Accel': 'C,P'}


class CivilPdf:
    def Activated(self):
        from safe.punch import export
        doc = FreeCAD.ActiveDocument
        filename = get_save_filename('.pdf')
        export.createPdf(doc, filename)

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_pdf",
            "Export to pdf")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_pdf",
            "export to pdf")
        rel_path = "Mod/Civil/safe/punch/icon/pdf.svg"
        path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(path):
            path = FreeCAD.ConfigGet("UserAppData") + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilPictur:
    def Activated(self):
        from safe.punch import export
        doc = FreeCAD.ActiveDocument
        i = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetInt("picture_ext", 0)
        ext = ('png', 'jpg', 'pdf')[i]
        filename = get_save_filename(f'.{ext}')
        export.createPdf(doc, filename)

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_pic",
            "Export to picture")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_pic",
            "export to picture")
        rel_path = "Mod/Civil/safe/punch/icon/png.png"
        path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(path):
            path = FreeCAD.ConfigGet("UserAppData") + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilExcel:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_excel",
            "Export to excel")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_excel",
            "export the result of punches to excel")
        rel_path = "Mod/Civil/safe/punch/icon/xlsx.png"
        path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(path):
            path = FreeCAD.ConfigGet("UserAppData") + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    def Activated(self):
        from safe.punch import export
        doc = FreeCAD.ActiveDocument
        punches = []
        for o in doc.Objects:
            if hasattr(o, "Proxy") and hasattr(o.Proxy, "Type"):
                if o.Proxy.Type == "Punch":
                    punches.append(o)
        filename = get_save_filename('.xlsx')
        export.to_excel(punches, filename)


    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilDxf:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_dxf",
            "Export to dxf")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_dxf",
            "export the result to dxf")
        rel_path = "Mod/Civil/safe/punch/Resources/icons/dxf.svg"
        path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(path):
            path = FreeCAD.ConfigGet("UserAppData") + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    def Activated(self):
        from safe.punch import export
        doc = FreeCAD.ActiveDocument
        # punches = []
        # for o in doc.Objects:
        #     if hasattr(o, "Proxy") and hasattr(o.Proxy, "Type"):
        #         if o.Proxy.Type == "Punch":
        #             punches.append(o)
        filename = get_save_filename('.dxf')
        export.to_dxf(doc, filename)


    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilHelp:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_help",
            "Help")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_help",
            "Help")
        path = str(
                   Path(civilwelcome.__file__).parent.absolute() / "Resources" / "icons" / "help.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    def Activated(self):
        import webbrowser
        path = str(
                   Path(civilwelcome.__file__).parent.absolute() / "safe" / "punch" / "Help.pdf"
                   )
        webbrowser.open_new(path)

    def IsActive(self):
        return True

class CivilUpdate:
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_update",
            "Update")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_update",
            "Update")
        path = str(
                   Path(civilwelcome.__file__).parent.absolute() / "Resources" / "icons" / "update.png"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    def Activated(self):
        import civil_update
        civil_update.update()

    def IsActive(self):
        return True




def get_save_filename(ext):
    from PySide2.QtWidgets import QFileDialog
    filters = f"{ext[1:]} (*{ext})"
    filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                              None, filters)
    if not filename:
        return
    if not ext in filename:
        filename += ext
    return filename


Gui.addCommand('Copy', Copy())
Gui.addCommand('Civil_pdf', CivilPdf())
Gui.addCommand('Civil_pic', CivilPictur())
Gui.addCommand('Civil_welcome', civilwelcome.CivilWelcome())
Gui.addCommand('Civil_excel', CivilExcel())
Gui.addCommand('Civil_help', CivilHelp())
Gui.addCommand('Civil_update', CivilUpdate())
Gui.addCommand('Civil_dxf', CivilDxf())

command_list = [
            "Copy",
            "Civil_pdf",
            "Civil_pic",
            "Civil_excel",
            "Civil_help",
            "Civil_dxf",
            "Civil_update",
            ]
