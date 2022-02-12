import os
from pathlib import Path
import PySide2
from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox
import FreeCAD
import FreeCADGui as Gui
import DraftTools
import civilwelcome

from safe.punch import (
    gui_punch,
    gui_slab,
    gui_beam,
    gui_base_foundation,
    gui_dxf,
    gui_automatic_strip,
    )

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
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "etabs.png"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        from safe.punch.py_widget import etabs_panel
        panel = etabs_panel.EtabsTaskPanel()
        Gui.Control.showDialog(panel)
        return panel

    def IsActive(self):
        return True

class CivilSafe1620:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_safe",
            "Export to Safe")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_safe",
            "Export Model to Safe")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "safe.png"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        allow, check = allowed_to_continue(
            'safe_export.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/0f14001cbbd16a23bfc8d2844d97947b/raw/',
            'punch',
            n=5,
            )
        if not allow:
            return
        from safe.punch.py_widget import safe_panel
        panel = safe_panel.Safe12TaskPanel()
        Gui.Control.showDialog(panel)
        show_warning_about_number_of_use(check)
        return panel

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class CivilForce:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_force",
            "Assign Force")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_force",
            "Assign force to foundation")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "force.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        from safe.punch.py_widget import force_panel
        panel = force_panel.ForceTaskPanel()
        Gui.Control.showDialog(panel)
        return panel

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilWall:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_wall",
            "Create wall")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_wall",
            "Create wall on foundation")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "wall.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        from safe.punch.py_widget import wall_panel
        panel = wall_panel.WallTaskPanel()
        Gui.Control.showDialog(panel)
        return panel

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilOpening:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil",
            "Add opening From Etabs")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil",
            "create an opening from selected points in etabs model")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "opening.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        from safe.punch import opening
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        etabs.set_current_unit('kN', 'mm')
        points = etabs.select_obj.get_selected_obj_type(1)
        if len(points) > 2:
            points_xyz = list(etabs.points.get_points_coords(points).values())
        height = 4000
        foun = None
        doc = FreeCAD.ActiveDocument
        if hasattr(doc, 'Foundation'):
            foun = doc.Foundation
            height = foun.height.Value
            z = foun.level.Value
        else:
            if hasattr(doc, 'Beam'):
                z = doc.Beam.start_point.z
        points_vec = [FreeCAD.Vector(p[0], p[1], z) for p in points_xyz]
        # wire = Draft.make_wire(points_vec)
        opening_obj = opening.make_opening(points_vec, height=height)
        if foun is not None:
            opening_objs = foun.openings + [opening_obj]
            foun.openings = opening_objs
        doc.recompute()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilExplodLoadPatterns:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_explode",
            "Explode Load Patterns")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_explode",
            "Explode Load Patterns")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "explode.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        allow, check = allowed_to_continue(
            'explode_loads.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/f05421c70967b698ca9016a1bdb54b01/raw',
            'punch',
            )
        if not allow:
            return
        from safe.punch.py_widget import explode_seismic_load_patterns
        panel = explode_seismic_load_patterns.Form()
        Gui.Control.showDialog(panel)
        show_warning_about_number_of_use(check)
        return panel

    def IsActive(self):
        return True


# class CivilCreateF2k:

#     def GetResources(self):
#         MenuText = QtCore.QT_TRANSLATE_NOOP(
#             "civil_create_f2k",
#             "Create F2k File")
#         ToolTip = QtCore.QT_TRANSLATE_NOOP(
#             "civil_create_f2k",
#             "Create F2k File")
#         path = str(
#                    Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "f2k.svg"
#                    )
#         return {'Pixmap': path,
#                 'MenuText': MenuText,
#                 'ToolTip': ToolTip}

#     def Activated(self):
#         from safe.punch.py_widget import create_f2k
#         import etabs_obj
#         etabs = etabs_obj.EtabsModel(backup=False)
#         panel = create_f2k.Form(etabs)
#         Gui.Control.showDialog(panel)
#         return panel

#     def IsActive(self):
#         return not FreeCAD.ActiveDocument is None

class CivilBaseFoundation:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_base_foundation",
            "Create base_foundation")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_base_foundation",
            "Create base of foundation")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "automatic_base_foundation.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        from safe.punch.py_widget import base_foundation_panel
        panel = base_foundation_panel.Form()
        Gui.Control.showDialog(panel)
        return panel

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class CivilFoundation:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "civil_foundation",
            "Create foundation")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "civil_foundation",
            "Create foundation")
        path = str(
                   Path(__file__).parent.absolute() / 'safe' / 'punch' / "Resources" / "icons" / "foundation.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

    def Activated(self):
        from safe.punch.py_widget import foundation_panel
        panel = foundation_panel.Form()
        Gui.Control.showDialog(panel)
        return panel

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

# class CivilChangeBranch:

#     def GetResources(self):
#         MenuText = QtCore.QT_TRANSLATE_NOOP(
#             "branch",
#             "Change branch")
#         ToolTip = QtCore.QT_TRANSLATE_NOOP(
#             "civil_change branch",
#             "Change branch")
#         path = str(
#                    Path(__file__).parent.absolute() / "Resources" / "icons" / "change_branch.svg"
#                    )
#         return {'Pixmap': path,
#                 'MenuText': MenuText,
#                 'ToolTip': ToolTip}

#     def Activated(self):
#         import change_branch
#         panel = change_branch.Form()
#         Gui.Control.showDialog(panel)
#         return panel

#     def IsActive(self):
#         return True


class CivilHelp:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_help",
            "Help")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_help",
            "Help")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "help.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    def Activated(self):
        import webbrowser
        path = str(
                   Path(__file__).parent.absolute() / "help" / "help.pdf"
                   )
        webbrowser.open_new(path)

    def IsActive(self):
        return True

# class CivilUpdate:
#     def GetResources(self):
#         MenuText = QtCore.QT_TRANSLATE_NOOP(
#             "Civil_update",
#             "Update")
#         ToolTip = QtCore.QT_TRANSLATE_NOOP(
#             "Civil_update",
#             "Update")
#         path = str(
#                    Path(__file__).parent.absolute() / "Resources" / "icons" / "update.png"
#                    )
#         return {'Pixmap': path,
#                 'MenuText': MenuText,
#                 'ToolTip': ToolTip}
#     def Activated(self):
#         import civil_update
#         civil_update.update()

#     def IsActive(self):
#         return True

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
                        n = 2,
                        ):
    import check_legal
    check = check_legal.CheckLegalUse(
                                filename,
                                gist_url,
                                dir_name,
                                n = n,
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
            Path(__file__).parent.absolute() / 'Resources' / 'ui' / 'serial.ui'
            )
        self.form = Gui.PySideUic.loadUi(serial_ui)


class RectangleSlab:
    """ RectangleSlab command definition.
    """

    def GetResources(self):

        return {'Pixmap'  : str(Path(__file__).parent.absolute() / 'safe' / 'punch' / 'Resources' / 'icons' / 'rectangle.svg'),
                'MenuText': "Draw Rectangle Slab",
                'ToolTip': "EXPERIMENTAL\nDraw Rectangle Slab.\nSelect 2 Punches to draw a slab between them."}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.punches = Gui.Selection.getSelection()
        self.continue_mode = False

        if len(self.punches) == 2:
            try:
                self.create_slab()
            except:
                self.create_by_selection()
        else:
            self.create_by_selection()

    def create_slab(self):
        punch1, punch2 = self.punches
        punches = []
        for o in (punch1, punch2):
            if hasattr(o, "Proxy") and \
                hasattr(o.Proxy, "Type") and \
                o.Proxy.Type == "Punch":
                punches.append(o)
        if len(punches) == 2:
            from safe.punch import rectangle_slab
            slab = rectangle_slab.make_rectangle_slab(punch1.center_of_load, punch2.center_of_load, width=1000, height=800)
            foun = FreeCAD.ActiveDocument.Foundation
            foun.tape_slabs = foun.tape_slabs + [slab]
            FreeCAD.ActiveDocument.recompute([foun, punch1, punch2])

    def create_by_selection(self):
        FreeCAD.Console.PrintMessage("Select the first punch"+ "\n")
        self.punches = []
        self.callback = Gui.Selection.addObserver(self)

    def addSelection(self, doc, obj, sub, pnt):
        Gui.Selection.removeObserver(self)
        if len(self.punches) == 0:
            FreeCAD.Console.PrintMessage("Select the second punch"+ "\n")
            self.punches.append(FreeCAD.getDocument(doc).getObject(obj))
            self.callback = Gui.Selection.addObserver(self)
        elif len(self.punches) == 1:
            self.punches.append(FreeCAD.getDocument(doc).getObject(obj))
            self.create_slab()
            self.punches = []
            if self.continue_mode:
                # TODO: fix continue mode according to Draft Commandsgit
                self.callback = Gui.Selection.addObserver(self)
            else:
                self.finish()

    def finish(self):
        if self.callback:
            Gui.Selection.removeObserver(self.callback)


Gui.addCommand('Civil_etabs', CivilEtabs())
Gui.addCommand('Civil_opening_etabs', CivilOpening())
Gui.addCommand('Civil_force', CivilForce())
Gui.addCommand('Civil_wall', CivilWall())
Gui.addCommand('civil_safe', CivilSafe1620())
Gui.addCommand('Copy', Copy())
Gui.addCommand('Civil_pdf', CivilPdf())
Gui.addCommand('Civil_pic', CivilPictur())
Gui.addCommand('Civil_welcome', civilwelcome.CivilWelcome())
Gui.addCommand('Civil_excel', CivilExcel())
Gui.addCommand('Civil_docx', CivilDocx())
Gui.addCommand('Civil_help', CivilHelp())
# Gui.addCommand('Civil_update', CivilUpdate())
# Gui.addCommand('Civil_branch', CivilChangeBranch())
Gui.addCommand('Civil_dxf', gui_dxf.OsafeDxf())
# Gui.addCommand('civil_explod_load_patterns', CivilExplodLoadPatterns())
# Gui.addCommand('create_f2k_file', CivilCreateF2k())
Gui.addCommand('automatic_base_foundation', CivilBaseFoundation())
Gui.addCommand('create_foundation', CivilFoundation())
Gui.addCommand('civil_slab', gui_slab.Slab())
Gui.addCommand('civil_beam', gui_beam.Beam())
Gui.addCommand('civil_base_foundation', gui_base_foundation.BaseFoundation())
Gui.addCommand('civil_punch', gui_punch.Punch())
Gui.addCommand('osafe_automatic_strip', gui_automatic_strip.OsafeAutomaticStrip())

command_list = [
            "Civil_etabs",
            "automatic_base_foundation",
            "create_foundation",
            "osafe_automatic_strip",
            "Civil_opening_etabs",
            'civil_punch',
            # 'civil_sketch',
            # "civil_explod_load_patterns",
            "Copy",
            # "Civil_update",
            # "Civil_branch",
            "Civil_help",
            ]

export_list = [
            "civil_safe",
            "Civil_pdf",
            "Civil_pic",
            "Civil_excel",
            "Civil_docx",
            "Civil_dxf",
            ]

draw_list = [
            "civil_base_foundation",
            "civil_beam",
            'civil_slab',
            ]
assign_list = [
            "Civil_force",
            "Civil_wall",
            ]

# draw_command_list = [
#         ''
# ]
