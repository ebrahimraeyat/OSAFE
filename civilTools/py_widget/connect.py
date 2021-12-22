from pathlib import Path
from PySide2.QtUiTools import loadUiType

cfactor_path = Path(__file__).absolute().parent.parent

connect_base, connect_window = loadUiType(cfactor_path / 'widgets' / 'connect.ui')

class ConnectForm(connect_base, connect_window):
    def __init__(self,
            etabs,
            parent=None):
        super(ConnectForm, self).__init__()
        self.setupUi(self)
        self.etabs = etabs
        self.SapModel = self.etabs.SapModel
        self.b1 = None
        self.b2 = None
        self.fill_points()
        self.create_connections()
        
    def create_connections(self):
        self.point_list1.itemClicked.connect(self.point_clicked)
        self.point_list2.itemClicked.connect(self.point_clicked)
        self.refresh_button.clicked.connect(self.fill_points)

    def point_clicked(self):
        self.SapModel.SelectObj.ClearSelection()
        p1 = self.point_list1.currentItem().text()
        p2 = self.point_list2.currentItem().text()
        self.SapModel.PointObj.SetSelected(p1, True)
        self.SapModel.PointObj.SetSelected(p2, True)
        self.SapModel.View.RefreshView()

    def fill_points(self):
        try:
            names = self.SapModel.SelectObj.GetSelected()[2]
        except IndexError:
            print('You must select at least two beam')
            return
        self.b1, self.b2 = names[:2]
        p1, p2, _ = self.SapModel.FrameObj.GetPoints(self.b1)
        p3, p4, _ = self.SapModel.FrameObj.GetPoints(self.b2)
        self.point_list1.clear()
        self.point_list2.clear()
        self.point_list1.addItems([p1, p2])
        self.point_list2.addItems([p3, p4])
        x1, y1 = self.SapModel.PointObj.GetCoordCartesian(p1)[:2]
        x2, y2 = self.SapModel.PointObj.GetCoordCartesian(p2)[:2]
        x3, y3 = self.SapModel.PointObj.GetCoordCartesian(p3)[:2]
        x4, y4 = self.SapModel.PointObj.GetCoordCartesian(p4)[:2]
        D = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if D == 0:
            print('Two lines are parallel!')
            return None
        xp = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / D
        yp = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / D
        d1 = self.etabs.points.get_distance_between_two_points_in_XY(p1, (xp, yp))
        d2 = self.etabs.points.get_distance_between_two_points_in_XY(p2, (xp, yp))
        d3 = self.etabs.points.get_distance_between_two_points_in_XY(p3, (xp, yp))
        d4 = self.etabs.points.get_distance_between_two_points_in_XY(p4, (xp, yp))
        if d1 < d2:
            self.point_list1.setCurrentRow(0)
        else:
            self.point_list1.setCurrentRow(1)
        if d3 < d4:
            self.point_list2.setCurrentRow(0)
        else:
            self.point_list2.setCurrentRow(1)

    def accept(self):
        p1 = self.point_list1.currentItem().text()
        p2 = self.point_list2.currentItem().text()
        self.etabs.frame_obj.connect_two_beams((self.b1, self.b2), (p1, p2))


