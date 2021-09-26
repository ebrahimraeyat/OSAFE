import os
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox
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
        path = str(Path(__file__).parent / 'safe' / 'punch' / "Resources" / "icons" / "pdf.svg")
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
        path = str(Path(__file__).parent / 'safe' / 'punch' / "Resources" / "icons" / "png.png")
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
        path = str(Path(__file__).parent / 'safe' / 'punch' / "Resources" / "icons" / "xlsx.png")
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
        path = str(Path(__file__).parent / 'safe' / 'punch' / "Resources" / "icons" / "dxf.svg")
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    
    def Activated(self):
        from safe.punch import export
        doc = FreeCAD.ActiveDocument
        filename = get_save_filename('.dxf')
        export.to_dxf(doc, filename)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilDocx:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_docx",
            "Export to Word")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_docx",
            "export the result to Word")
        path = str(Path(__file__).parent / 'safe' / 'punch' / "Resources" / "icons" / "word.png")
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    
    def Activated(self):
        allow, check = allowed_to_continue(
            'punch_docx.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/b45fcd6577c27e5f89390b1c5eef0d1f/raw',
            'punch'
            )
        if not allow:
            return
        from safe.punch import report
        doc = FreeCAD.ActiveDocument
        filename = get_save_filename('.docx')
        report.create_punches_report(doc, filename)
        show_warning_about_number_of_use(check)

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilEtabs:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_etabs",
            "Import From Etabs")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_etabs",
            "Read Data From Etabs")
        path = str(
                   Path(civilwelcome.__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "etabs.png"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    
    def Activated(self):
        allow, check = allowed_to_continue(
            'punch_etabs.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/9f32da1884e7b3f1a605e12d292c4fd0/raw',
            'punch'
            )
        if not allow:
            return
        from safe.punch.py_widget import etabs_panel
        panel = etabs_panel.EtabsTaskPanel()
        Gui.Control.showDialog(panel)
        show_warning_about_number_of_use(check)
        return panel

    def IsActive(self):
        return True


class CivilOpeningEtabs:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil",
            "Add openning From Etabs")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil",
            "create an opening from selected points in etabs model")
        path = str(
                   Path(civilwelcome.__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "opening.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    
    def Activated(self):
        from safe.punch import opening
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        points = etabs.select_obj.get_selected_obj_type(1)
        if len(points) > 2:
            points_xyz = list(etabs.points.get_points_coords(points).values())
        points_xy0 = [(p[0], p[1], 0) for p in points_xyz]
        points_vec = [FreeCAD.Vector(*p) for p in points_xy0]
        opening.make_opening(points=points_vec)

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
                   Path(civilwelcome.__file__).parent.absolute() / "help" / "help.pdf"
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

def allowed_to_continue(
                        filename,
                        gist_url,
                        dir_name,
                        ):
    import check_legal
    check = check_legal.CheckLegal(
                                filename,
                                gist_url,
                                dir_name,
    )
    allow, text = check.allowed_to_continue()
    if allow and not text:
        return True, check
    else:
        if text in ('INTERNET', 'SERIAL'):
            ui = SerialForm()
            ui.form.serial.setText(check.serial)
            Gui.Control.showDialog(ui)
            # if ui.setupUi():
            #     Gui.Control.closeDialog(ui)
            return False, check
        elif text == 'REGISTERED':
            msg = "Congrajulation! You are now registered, enjoy using this features!"
            QMessageBox.information(None, 'Registered', str(msg))
            return True, check
    return False, check

def show_warning_about_number_of_use(check):
    check.add_using_feature()
    _, no_of_use = check.get_registered_numbers()
    n = check.n - no_of_use
    if n > 0:
        msg = f"You can use this feature {n} more times!\n then you must register the software."
        QMessageBox.warning(None, 'Not registered!', str(msg))

class SerialForm:
    def __init__(self):
        serial_ui = str(
            Path(civilwelcome.__file__).parent.absolute() / 'Resources' / 'ui' / 'serial.ui'
            )
        self.form = Gui.PySideUic.loadUi(serial_ui)

Gui.addCommand('Civil_etabs', CivilEtabs())
Gui.addCommand('Civil_opening_etabs', CivilOpeningEtabs())
Gui.addCommand('Copy', Copy())
Gui.addCommand('Civil_pdf', CivilPdf())
Gui.addCommand('Civil_pic', CivilPictur())
Gui.addCommand('Civil_welcome', civilwelcome.CivilWelcome())
Gui.addCommand('Civil_excel', CivilExcel())
Gui.addCommand('Civil_docx', CivilDocx())
Gui.addCommand('Civil_help', CivilHelp())
Gui.addCommand('Civil_update', CivilUpdate())
Gui.addCommand('Civil_dxf', CivilDxf())

command_list = [
            "Civil_etabs",
            "Civil_opening_etabs",
            "Copy",
            "Civil_pdf",
            "Civil_pic",
            "Civil_excel",
            "Civil_docx",
            "Civil_dxf",
            "Civil_update",
            "Civil_help",
            ]
