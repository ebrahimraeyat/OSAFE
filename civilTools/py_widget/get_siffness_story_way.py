from pathlib import Path

from PyQt5 import uic

cfactor_path = Path(__file__).absolute().parent.parent

stiffness_base, stiffness_window = uic.loadUiType(cfactor_path / 'widgets' / 'get_siffness_story_way.ui')

class ChooseStiffnessForm(stiffness_base, stiffness_window):
    def __init__(self, parent=None):
        super(ChooseStiffnessForm, self).__init__()
        self.setupUi(self)
