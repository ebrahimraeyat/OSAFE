from pathlib import Path

from PyQt5 import uic, QtGui

cfactor_path = Path(__file__).absolute().parent.parent.parent

wall_load_base, wall_load_window = uic.loadUiType(cfactor_path / 'widgets' / 'assing' / 'wall_load_on_frames.ui')

class WallLoadForm(wall_load_base, wall_load_window):
    LOADTYPE = {'Force' : 1, 'Moment': 2}
    def __init__(self, etabs_model, parent=None):
        super(WallLoadForm, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.fill_widget()
        self.create_connections()

    def fill_widget(self):
        stories = self.etabs.SapModel.Story.GetNameList()[1]
        self.stories.addItems(stories)
        self.select_all_stories()
        load_patterns = self.etabs.load_patterns.get_load_patterns()
        self.loadpat.addItems(load_patterns)

    def select_all_stories(self):
        for i in range(self.stories.count()):
            item = self.stories.item(i)
            item.setSelected(True)

    def create_connections(self):
        self.auto_height.clicked.connect(self.reset_widget)
        self.override_height.clicked.connect(self.reset_widget)
        self.relative.clicked.connect(self.set_dists_range)
        self.buttonBox.clicked.connect(self.handleButtonClick)

    def handleButtonClick(self, button):
        sb = self.buttonBox.standardButton(button)
        if sb == QtGui.QDialogButtonBox.Apply:
            self.accept()

    def set_dists_range(self):
        if self.relative.isChecked():
            self.dist1.setRange(0, 1)
            self.dist2.setRange(0, 1)
        else:
            self.dist1.setRange(0, 30)
            self.dist2.setRange(0, 30)

    def reset_widget(self):
        if self.auto_height.isChecked():
            self.none_beam_h.setEnabled(True)
            self.height.setEnabled(False)
        elif self.override_height.isChecked():
            self.none_beam_h.setEnabled(False)
            self.height.setEnabled(True)

    def accept(self):
        loadpat = self.loadpat.currentText()
        mass_per_area = self.mass.value()
        if self.override_height.isChecked():
            height = self.height.value()
        else:
            height = None
        stories = [item.text() for item in self.stories.selectedItems()]
        none_beam_h = self.none_beam_h.value()
        dist1 = self.dist1.value()
        dist2 = self.dist2.value()
        relative = self.relative.isChecked()
        load_type = WallLoadForm.LOADTYPE[self.load_type.currentText()]
        replace = self.replace.isChecked()
        parapet_wall_height = self.parapet_wall_height.value()
        height_from_below = self.height_from_below.isChecked()
        opening_ratio = self.opening_ratio.value()
        names = None
        item_type = 0
        self.etabs.frame_obj.assign_gravity_load_to_selfs_and_above_beams(
            loadpat,
            mass_per_area,
            dist1,
            dist2,
            names,
            stories,
            load_type,
            relative,
            replace,
            item_type,
            height,
            none_beam_h,
            parapet_wall_height,
            height_from_below,
            opening_ratio,
        )