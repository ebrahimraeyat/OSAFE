from asyncore import write
from pathlib import Path
from typing import Iterable

# import FreeCAD
import FreeCADGui as Gui

from osafe_py_widgets import resource_rc
from PySide2.QtGui import QPixmap

punch_path = Path(__file__).parent.parent


class Form:
    def __init__(self, etabs, parent=None):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'osafe_widgets' / 'create_f2k.ui'))
        self.etabs = etabs
        filename = Path(self.etabs.SapModel.GetModelFilename()).with_suffix('.F2k')
        self.form.filename.setText(str(filename))
        self.create_connections()

    def create_connections(self):
        self.form.start_button.clicked.connect(self.accept)
        self.form.browse.clicked.connect(self.browse)
        self.form.close_button.clicked.connect(self.reject)

    def reject(self):
        Gui.Control.closeDialog()

    def browse(self):
        ext = '.f2k'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)

    def accept(self):
        filename = self.form.filename.text()
        import create_f2k
        writer = create_f2k.CreateF2kFile(
            input_f2k=Path(filename),
            etabs=self.etabs,
            load_cases=[],
            case_types=[],
            model_datum=0,
            append=True,
            )
        if self.form.load_combinations.isChecked():
            types = []
            if self.form.linear_add.isChecked():
                types.append('Linear Add')
            if self.form.envelope.isChecked():
                types.append('Envelop')
            if types:
                writer.add_load_combinations(types=tuple(types))
                writer.write()
                self.reject()
            
        # if FreeCAD.ActiveDocument:
        #     safe = FreeCAD.ActiveDocument.Safe
        #     if safe:
        #         safe.input = filename
        #         # safe.output = f
        
        # pixmap = QPixmap(str(punch_path / 'Resources' / 'icons' / 'tick.svg'))
        # d = {
        #     1 : self.form.one,
        #     2 : self.form.two,
        #     3 : self.form.three,
        #     4 : self.form.four,
        #     5 : self.form.five,
        # }
        # for ret in writer.create_f2k():
        #     if type(ret) == tuple and len(ret) == 3:
        #         message, percent, number = ret
        #         if type(message) == str and type(percent) == int:
        #             self.form.result_label.setText(message)
        #             self.form.progressbar.setValue(percent)
        #             if number < 6:
        #                 d[number].setPixmap(pixmap)
        #     elif type(ret) == bool:
        #         if not ret:
        #             self.form.result_label.setText("Error Occurred, process did not finished.")
        #         self.form.start_button.setEnabled(False)
        #     elif type(ret) == str:
        #         self.form.result_label.setText(ret)
    
    def add_load_combinations(
                self,
                types: Iterable = ('Envelope', 'Linear Add'),
        ):
        self.etabs.load_cases.select_all_load_cases()
        table_key = "Load Combination Definitions"
        cols = ['Name', 'LoadName', 'Type', 'SF']
        df = self.etabs.database.read(table_key, to_dataframe=True, cols=cols)
        df.fillna(method='ffill', inplace=True)
        # design_load_combinations = set()
        # for type_ in ('concrete', 'steel', 'shearwall', 'slab'):
        #     load_combos_names = self.etabs.database.get_design_load_combinations(type_)
        #     if load_combos_names is not None:
        #         design_load_combinations.update(load_combos_names)
        # filt = df['Name'].isin(design_load_combinations)
        filt = df['Type'].isin(types)
        df = df.loc[filt]
        df.replace({'Type': {'Linear Add': '"Linear Add"'}}, inplace=True)

        d = {
            'Name': 'Combo=',
            'LoadName': 'Load=',
            'Type' : 'Type=',
            'SF' : 'SF=',
            }
        content = self.add_assign_to_fields_of_dataframe(df, d)
        return content

    @staticmethod
    def add_assign_to_fields_of_dataframe(
        df,
        assignment : dict,
        content : bool = True,
        ):
        '''
        adding a prefix to each member of dataframe for example:
        LIVE change to Type=LIVE
        content : if content is True, the string of dataframe return
        '''
        for col, pref in assignment.items():
            df[col] = pref + df[col].astype(str)
        if content:
            return df.to_string(header=False, index=False)
        return df

