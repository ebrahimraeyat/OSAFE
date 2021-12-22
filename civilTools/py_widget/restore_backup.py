from pathlib import Path

from PyQt5 import uic

cfactor_path = Path(__file__).absolute().parent.parent
restore_base, restore_window = uic.loadUiType(cfactor_path / 'widgets' / 'restore_backup.ui')

class ListForm(restore_base, restore_window):
    def __init__(self, etabs_model, parent=None):
        super(ListForm, self).__init__(parent)
        self.setupUi(self)
        self.etabs = etabs_model
        self.fill_list()

    def accept(self):
        item = self.list.currentItem()
        filename_path = self.file_path / item.text()
        self.etabs.restore_backup(filename_path)
        super(ListForm, self).accept()

    def fill_list(self):
        self.file_path = self.etabs.get_filepath()
        edbs = self.file_path.glob(f'BACKUP_*')
        edbs = [edb.name for edb in edbs]
        self.list.addItems(edbs)
        filename = self.etabs.get_file_name_without_suffix()
        file_path = self.etabs.get_filepath()
        max_num = 0
        for edb in file_path.glob(f'BACKUP_{filename}*.EDB'):
            num = edb.name.rstrip('.EDB')[len('BACKUP_') + len(filename) + 1:]
            try:
                num = int(num)
                max_num = max(max_num, num)
            except:
                continue
        name = f'BACKUP_{filename}_{max_num}.EDB'
        if not name.lower().endswith('.edb'):
            name += '.EDB'
        i = -1
        try:
            i = edbs.index(name)
        except ValueError:
            i = len(edbs) - 1
        self.list.setCurrentRow(i)

