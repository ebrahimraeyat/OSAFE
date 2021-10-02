if __name__ == '__main__':
    import sys
    FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
    sys.path.append(FREECADPATH)

import FreeCAD
import Part

__all__ = ['Area']


class Area:
    def __init__(
                self,
                etabs=None,
                ):
        self.etabs = etabs
        self.SapModel = etabs.SapModel

    def export_freecad_slabs(self, doc : 'App.Document'):
        self.etabs.set_current_unit('kN', 'mm')
        foun = doc.Foundation
        if foun.foundation_type == 'Strip':
            slabs = foun.tape_slabs
            for slab in slabs:
                points = slab.points
                self.create_area_by_coord(points)
        elif foun.foundation_type == 'Mat':
            points = []
            edges = Part.__sortEdges__(foun.plane_without_openings.Edges)
            for e in edges:
                v = e.firstVertex()
                points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
            self.create_area_by_coord(points)


    def create_area_by_coord(self, points : 'Base.Vector'):
        n = len(points)
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        zs = [p.z for p in points]
        self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)

    def export_freecad_openings(self, openings):
        for opening in openings:
            points = opening.points
            n = len(points)
            xs = [p.x for p in points]
            ys = [p.y for p in points]
            zs = [p.z for p in points]
            ret = self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)
            name = ret[3]
            self.SapModel.AreaObj.SetOpening(name, True)


if __name__ == '__main__':
    import sys
    from pathlib import Path

    FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
    sys.path.append(FREECADPATH)
    import FreeCAD
    if FreeCAD.GuiUp:
        document = FreeCAD.ActiveDocument
    else:
        filename = Path(__file__).absolute().parent.parent / 'test' / 'etabs_api' / 'test_files' / 'freecad' / 'mat.FCStd'
        document= FreeCAD.openDocument(str(filename))
    slabs = document.Foundation.tape_slabs
    openings = document.Foundation.openings

    current_path = Path(__file__).parent
    sys.path.insert(0, str(current_path))
    from etabs_obj import EtabsModel
    etabs = EtabsModel(backup=False, software='SAFE')
    SapModel = etabs.SapModel
    ret = etabs.area.export_freecad_slabs(document)
    ret = etabs.area.export_freecad_openings(openings)
    print('Wow')