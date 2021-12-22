from pathlib import Path

from PyQt5 import uic

cfactor_path = Path(__file__).absolute().parent.parent
base, window = uic.loadUiType(cfactor_path / 'widgets' / 'delete_backups.ui')

class ListForm(base, window):
    def __init__(self, etabs_model, parent=None):
        super(ListForm, self).__init__(parent)
        self.setupUi(self)
        self.etabs = etabs_model
        self.fill_list()
        self.create_connections()

    def create_connections(self):
        self.select_all.clicked.connect(self.set_list_items_selected)
        self.deselect_all.clicked.connect(self.set_list_items_selected)
        self.delete_button.clicked.connect(self.accept)

    def accept(self):
        items = self.list.selectedItems()
        for item in items:
            filename_path = self.file_path / item.text()
            filename_path.unlink()
            self.list.removeItemWidget(item)
        self.list.clear()
        self.fill_list()
        self.set_list_items_selected(False)
        window.accept(self)

    def fill_list(self, select=True):
        self.file_path = self.etabs.get_filepath()
        edbs = self.file_path.glob(f'BACKUP_*')
        edbs = [edb.name for edb in edbs]
        self.list.addItems(edbs)
        self.set_list_items_selected(select)
        

    def set_list_items_selected(self, select=True):
        button = self.sender()
        if button.objectName() == 'select_all':
            select = True
        elif button.objectName() == 'deselect_all':
            select = False
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setSelected(select)
