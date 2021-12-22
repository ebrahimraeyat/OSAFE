import sys
from pathlib import Path

from PyQt5 import QtCore

from PyQt5 import uic
from PyQt5.QtCore import Qt

cfactor_path = Path(__file__).absolute().parent.parent
# civiltools_path = cfactor_path.parent.parent
# sys.path.insert(0, civiltools_path)
# from etabs_api import etabs_obj

story_base, story_window = uic.loadUiType(cfactor_path / 'widgets' / 'drift.ui')

class StoryForm(story_base, story_window):
    def __init__(self, etabs_model, stories, parent=None):
        super(StoryForm, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        self.stories = stories
        self.fill_top_bot_stories()
        self.fill_height_and_no_of_stories()
        self.fill_xy_loadcase_names()
        self.create_connections()

    def fill_xy_loadcase_names(self):
        x_names, y_names = self.etabs.load_patterns.get_load_patterns_in_XYdirection()
        drift_load_patterns = self.etabs.load_patterns.get_drift_load_pattern_names()
        all_load_case = self.etabs.SapModel.Analyze.GetCaseStatus()[1]
        x_names = set(x_names).intersection(set(all_load_case))
        y_names = set(y_names).intersection(set(all_load_case))
        self.x_loadcase_list.addItems(x_names)
        self.y_loadcase_list.addItems(y_names)
        items = []
        for lw in (self.x_loadcase_list, self.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
        for name in drift_load_patterns:
            if name in x_names:
                matching_items = self.x_loadcase_list.findItems(name, Qt.MatchExactly)
            elif name in y_names:
                matching_items = self.y_loadcase_list.findItems(name, Qt.MatchExactly)
            for item in matching_items:
                item.setCheckState(Qt.Checked)

    def fill_top_bot_stories(self):
        for combo_box in (
            self.bot_x_combo,
            self.top_x_combo,
            # self.bot_y_combo,
            # self.top_y_combo,
        ):
            combo_box.addItems(self.stories)
        n = len(self.stories)
        self.bot_x_combo.setCurrentIndex(0)
        self.top_x_combo.setCurrentIndex(n - 2)
        # self.bot_y_combo.setCurrentIndex(0)
        # self.top_y_combo.setCurrentIndex(n - 2)

    def create_connections(self):
        self.bot_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.top_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        # self.bot_y_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        # self.top_y_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)

    def fill_height_and_no_of_stories(self):
        bot_story_x = bot_story_y = self.bot_x_combo.currentText()
        top_story_x = top_story_y = self.top_x_combo.currentText()
        # bot_story_y = self.bot_y_combo.currentText()
        # top_story_y = self.top_y_combo.currentText()
        bot_level_x, top_level_x, bot_level_y, top_level_y = self.etabs.story.get_top_bot_levels(
                bot_story_x, top_story_x, bot_story_y, top_story_y, False
                )
        hx, hy = self.etabs.story.get_heights(bot_story_x, top_story_x, bot_story_y, top_story_y, False)
        nx, ny = self.etabs.story.get_no_of_stories(bot_level_x, top_level_x, bot_level_y, top_level_y)
        self.no_story_x_spinbox.setValue(nx)
        # self.no_story_y_spinbox.setValue(ny)
        self.height_x_spinbox.setValue(hx)
        # self.height_y_spinbox.setValue(hy)

