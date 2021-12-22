from pathlib import Path
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox

cfactor_path = Path(__file__).absolute().parent.parent.parent

base, window = uic.loadUiType(cfactor_path / 'widgets' / 'tools' / 'distance_between_two_points.ui')

class Form(base, window):
    def __init__(self,
            etabs,
            parent=None):
        super(Form, self).__init__()
        self.setupUi(self)
        self.etabs = etabs
        self.fill_points()
        self.show_button.clicked.connect(self.show_points)
    
    def show_points(self):
        if len(self.point_list) == 0:
            return
        p1 = self.point_list.item(0).text()
        p2 = self.point_list.item(1).text()
        self.etabs.SapModel.SelectObj.ClearSelection()
        self.etabs.SapModel.PointObj.SetSelected(p1, True)
        self.etabs.SapModel.PointObj.SetSelected(p2, True)
        self.etabs.SapModel.View.RefreshView()

    def fill_points(self):
        points_names = self.etabs.select_obj.get_selected_obj_type(1)
        line_name = self.etabs.select_obj.get_selected_obj_type(2)
        if points_names is None and line_name is None:
            message = 'Please Select Two Points or a Frame in ETBAS Model.'
            QMessageBox.information(None, 'Selection', message)
            return
        if len(points_names) < 2 and not line_name:
            return
        if len(points_names) > 1:
            p1, p2 = points_names[:2]
        else:
            p1, p2, _ = self.etabs.SapModel.FrameObj.GetPoints(line_name[0])
        self.point_list.clear()
        self.point_list.addItems([p1, p2])
        return True

    def accept(self):
        ret = self.fill_points()
        if ret is None:
            return
        p1 = self.point_list.item(0).text()
        p2 = self.point_list.item(1).text()
        self.etabs.set_current_unit('N', 'm')
        distance = self.etabs.points.get_distance_between_two_points_in_XY(p1, p2)
        self.dist.setValue(distance)
        self.etabs.SapModel.SelectObj.ClearSelection()
        self.etabs.SapModel.View.RefreshView()


