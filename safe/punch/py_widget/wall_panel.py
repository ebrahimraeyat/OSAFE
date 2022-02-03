from pathlib import Path

import FreeCAD
import FreeCADGui as Gui
import ArchWall

punch_path = Path(__file__).parent.parent


class WallTaskPanel:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'wall_panel.ui'))
        self.fill_load_patterns()
        self.create_connections()

    def fill_load_patterns(self):
        if hasattr(FreeCAD, 'load_cases'):
            self.form.loadpat.addItems(FreeCAD.load_cases)
        else:
            pass

    def create_connections(self):
        self.form.create_button.clicked.connect(self.create_wall)

    def create_wall(self):
        sel = Gui.Selection.getSelection()
        slabs = []
        for s in sel:
            if (hasattr(s, "Proxy") and
                hasattr(s.Proxy, "Type") and
                s.Proxy.Type == "Beam"
                ):
                slabs.append(s)
        if not slabs:
            return None
        weight = self.form.weight.value()
        height = self.form.height_box.value()
        create_blocks = self.form.create_blocks.isChecked()
        loadpat = self.form.loadpat.currentText()
        mat = FreeCAD.ActiveDocument.findObjects(Type='App::MaterialObjectPython')
        if not mat:
            import Arch
            mat =  Arch.makeMaterial('Bricks')
            mat.Color = (0.89, .89, 0.)
        else:
            mat = mat[0]
        for s in slabs:
            wall = ArchWall.makeWall(baseobj=s,height=height * 1000)
            wall.addProperty('App::PropertyInteger', 'weight', 'Wall')
            wall.addProperty('App::PropertyString', 'loadpat', 'Wall')
            wall.loadpat = loadpat
            wall.weight = weight
            wall.Base.ViewObject.Visibility = True
            wall.Material = mat
            wall.Width = 300
            if create_blocks:
                wall.MakeBlocks = True
                wall.BlockHeight = 400
                wall.BlockLength = 800
                wall.OffsetSecond = 400
                wall.Joint = 40
                wall.ViewObject.DisplayMode = 'Flat Lines'
                wall.ViewObject.LineWidth = 1
            else:
                wall.ViewObject.DisplayMode = 'Shaded'
                wall.ViewObject.Transparency = 60
        FreeCAD.ActiveDocument.recompute()
