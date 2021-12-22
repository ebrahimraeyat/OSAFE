from pathlib import Path

from PySide2 import uic

civiltools_path = Path(__file__).absolute().parent.parent

StyleSheet = '''
#RedProgressBar {
    text-align: center;
    border-radius: 8px;
}
#RedProgressBar::chunk {
    background-color: #F44336;
    border-radius: 8px;
}
#GreenProgressBar {
    min-height: 12px;
    max-height: 12px;
    border-radius: 6px;
}
#GreenProgressBar::chunk {
    border-radius: 6px;
    background-color: #009688;
}
#BlueProgressBar {
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
}
#BlueProgressBar::chunk {
    background-color: #2196F3;
    width: 10px; 
    margin: 0.5px;
}
'''

update_base, update_window = uic.loadUiType(civiltools_path / 'widgets' / 'update.ui')


class UpdateWindow(update_base, update_window):

    def __init__(self, parent=None):
        super(UpdateWindow, self).__init__()
        self.setStyleSheet(StyleSheet)
        self.setupUi(self)