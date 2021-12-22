from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog

cfactor_path = Path(__file__).absolute().parent.parent

stiffness_base, stiffness_window = uic.loadUiType(cfactor_path / 'widgets' / 'show_siffness_story_way.ui')

class ChooseStiffnessForm(stiffness_base, stiffness_window):
    def __init__(self, parent=None):
        super(ChooseStiffnessForm, self).__init__()
        self.setupUi(self)
        self.radio_button_file.toggled.connect(self.file_toggled)
        self.browse_push_button.clicked.connect(self.get_file_name)

    def file_toggled(self):
        if self.radio_button_file.isChecked():
            self.json_line_edit.setEnabled(True)
            self.browse_push_button.setEnabled(True)
        else:
            self.json_line_edit.setEnabled(False)
            self.browse_push_button.setEnabled(False)

    def get_file_name(self):
        from pathlib import Path
        import comtypes.client
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        if not etabs:
            directory = ''
        else:
            SapModel = etabs.SapModel
            directory = str(Path(SapModel.GetModelFilename()).parent.absolute())
        filename, _ = QFileDialog.getOpenFileName(self, 'load stiffness',
                                                  directory, "json(*.json)")
        if filename == '':
            return
        self.json_line_edit.setText(filename)


