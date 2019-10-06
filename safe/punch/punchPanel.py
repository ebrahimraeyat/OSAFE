import re
import os
import FreeCADGui as Gui
import FreeCAD as App
# from PySide import QtGui, QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from safe.punch import geom
from safe.punch import pdf
# from safe.punch.colorbar import ColorMap
punch_path = os.path.split(os.path.abspath(__file__))[0]


class PunchTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.lastDirectory = ''
        App.newDocument("punch")

    def setupUi(self):
        # self.createWidgetsOne()
        self.create_connections()
        icon_path = punch_path + '/icon'
        self.form.export_excel_button.setIcon(QPixmap(icon_path + "/xlsx.png"))
        self.form.export_pdf_button.setIcon(QPixmap(icon_path + "/pdf.svg"))
        self.form.export_image_button.setIcon(QPixmap(icon_path + "/png.png"))
        self.form.calculate_punch_button.setIcon(QPixmap(icon_path + "/run.svg"))
        self.form.help_button.setIcon(QPixmap(icon_path + "/help.svg"))
        self.form.update_button.setIcon(QPixmap(icon_path + "/update.png"))

    def create_connections(self):
        self.form.excel_button.clicked.connect(self.on_browse)
        self.form.excel_lineedit.textChanged.connect(self.update_shape)
        self.form.calculate_punch_button.clicked.connect(self.calculate_punch)
        self.form.export_excel_button.clicked.connect(self.export_to_excel)
        self.form.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.form.export_image_button.clicked.connect(self.export_to_image)
        self.form.help_button.clicked.connect(self.help)
        self.form.update_button.clicked.connect(self.update)

    def clearAll(self):
        doc = App.ActiveDocument
        if doc is None:
            return
        objs = doc.Objects
        if objs:
            group = objs[0]
            group.removeObjectsFromDocument()
            doc.removeObject(group.Label)

    def update_shape(self):
        filename = self.form.excel_lineedit.text()
        # ACI2019 = self.form.ACI2019_checkbox.isChecked()
        self.shape = geom.Geom(filename, self.form)
        combos = self.shape.load_combinations['Combo'].unique()
        self.form.load_combination_box.addItems(list(combos))
        self.form.safe_prop_browser.setText(self.shape._safe.__str__())
        self.shape.plot()
        self.form.calculate_punch_button.setEnabled(True)

    def calculate_punch(self):
        self.ratios_df = self.shape.punch_ratios()
        # self.add_color_map()
        self.form.export_excel_button.setEnabled(True)
        self.form.export_pdf_button.setEnabled(True)
        self.form.export_image_button.setEnabled(True)

    # def add_color_map(self):
    #     ratios = self.ratios_df.loc['Max']
    #     min_ = ratios.min()
    #     max_ = ratios.max()
    #     mw = Gui.getMainWindow()  # access the main window
    #     ColorMapWidget = QDockWidget()  # create a new dockwidget
    #     ColorMapWidget.setWidget(ColorMap(min_, max_))  # load the Ui script
    #     mw.addDockWidget(Qt.RightDockWidgetArea, ColorMapWidget)  # add the widget to the main window

    def on_browse(self):
        self.form.bar_label.setText('Reading excel file ...')
        filename = self.getFilename(['xls', 'xlsx'])
        if not filename:
            self.form.bar_label.setText('')
            return

        self.form.excel_lineedit.setText(filename)

    def help(self):
        import webbrowser
        webbrowser.open_new(punch_path + '/Help.pdf')

    def export_to_excel(self):
        filters = "Excel (*.xlsx)"
        filename, _ = QFileDialog.getSaveFileName(self.form, 'select file',
                                                  self.lastDirectory, filters)
        if not filename:
            return
        if not '.xlsx' in filename:
            filename += ".xlsx"
        self.ratios_df.to_excel(filename)

    def export_to_pdf(self):
        filename = self.get_save_filename('.pdf')
        doc = App.ActiveDocument
        pdf.createPdf(doc, filename)

    def export_to_image(self):
        ext = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetInt("picture_ext", 0)
        ext = ('png', 'jpg', 'pdf')[i]
        filename = self.get_save_filename(f'.{ext}')
        doc = App.ActiveDocument
        pdf.createPdf(doc, filename)

    def getLastSaveDirectory(self, f):
        return os.sep.join(f.split(os.sep)[:-1])

    def getFilename(self, prefixes):
        filters = 'Excel ('
        for prefix in prefixes:
            filters += f"*.{prefix} "
        filters += ')'
        filename, _ = QFileDialog.getOpenFileName(self.form, 'select file',
                                                  self.lastDirectory, filters)
        if not filename:
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename

    def get_save_filename(self, ext):
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(self.form, 'select file',
                                                  self.lastDirectory, filters)
        if not filename:
            return
        if not ext in filename:
            filename += ext
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename

    def update(self):
        if (QMessageBox.question(None, "update", "update to latest version?!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.No):
            return
        if not internet():
            msg = "You are not connected to the Internet, please check your internet connection."
            QMessageBox.warning(None, 'update', str(msg))
            return

        civil_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
        user_data_dir = FreeCAD.getUserAppDataDir()
            if not user_data_dir in civil_path:
                mod_path = os.path.join(FreeCAD.getUserAppDataDir(), 'Mod')
                if not os.path.exists(mod_path):
                    os.mkdir(mod_path)
                civil_path = os.path.join(mod_path, 'Civil')
        import git
        g = git.cmd.Git(civil_path)
        msg = ''
        try:
            msg = g.pull(env={'GIT_SSL_NO_VERIFY': '1'})
        except:
            QMessageBox.information(None, "update", "update takes some minutes, please be patient.")
            import shutil
            import tempfile
            default_tmp_dir = tempfile._get_default_tempdir()
            name = next(tempfile._get_candidate_names())
            punch_temp_dir = os.path.join(default_tmp_dir, 'Civil' + name)
            os.mkdir(punch_temp_dir)
            os.chdir(punch_temp_dir)
            git.Git('.').clone("https://github.com/ebrahimraeyat/Civil.git", env={'GIT_SSL_NO_VERIFY': '1'})
            # shutil.rmtree(civil_path, onerror=onerror)
            src_folder = os.path.join(punch_temp_dir, 'Civil')

            shutil.copytree(src_folder, civil_path)
            msg = 'update done successfully, please remove Civil folder from FreeCAD installation folder!,  then restart FreeCAD.'

        else:
            if not msg:
                msg = 'error occurred during update\nplease contact with @roknabadi'
        # msg += '\n please restart the program.'
        QMessageBox.information(None, 'update', msg)


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        print('another error')
        raise


def internet(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        #         print(ex.message)
        return False


if __name__ == '__main__':
    panel = PunchTaskPanel()
