from pathlib import Path

from PyQt5 import uic

cfactor_path = Path(__file__).absolute().parent.parent.parent

base, window = uic.loadUiType(cfactor_path / 'widgets' / 'assing' / 'assign_frame_sections.ui')

class Dialog(base, window):
    def __init__(self, etabs_model, parent=None):
        super(Dialog, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.fill_stories()
        self.beam_names = self.etabs.frame_obj.concrete_section_names('Beam')
        self.column_names = self.etabs.frame_obj.concrete_section_names('Column')
        self.other_names = self.etabs.frame_obj.other_sections(self.beam_names + self.column_names)
        self.fill_sections()
        self.create_connections()

    def fill_stories(self):
        stories = self.etabs.SapModel.Story.GetNameList()[1]
        self.stories.addItems(stories)
        self.select_all_stories()

    def fill_sections(self):
        self.sections.clear()
        if self.all_sections.isChecked():
            self.sections.addItems(self.other_names)
        elif self.beams.isChecked():
            self.sections.addItems(self.beam_names)
        elif self.columns.isChecked():
            self.sections.addItems(self.column_names)

    def select_all_stories(self):
        for i in range(self.stories.count()):
            item = self.stories.item(i)
            item.setSelected(True)

    def create_connections(self):
        self.all_sections.clicked.connect(self.fill_sections)
        self.beams.clicked.connect(self.fill_sections)
        self.columns.clicked.connect(self.fill_sections)
        self.assign_button.clicked.connect(self.accept)
        self.filter_line.textChanged.connect(self.filter_sections)
        self.close_button.clicked.connect(self.reject)

    def filter_sections(self):
        text = self.filter_line.text()
        for i in range(self.sections.count()):
            item = self.sections.item(i)
            item.setHidden(not (item.text().__contains__(text)))

    def accept(self):
        stories = [item.text() for item in self.stories.selectedItems()]
        sec_name = self.sections.currentItem().text()
        sec_type = 'other'
        if self.beams.isChecked():
            sec_type = 'beam'
        elif self.columns.isChecked():
            sec_type = 'column'
        self.etabs.frame_obj.assign_sections_stories(
            sec_name = sec_name,
            stories = stories,
            frame_names = None,
            sec_type = sec_type,
            )
