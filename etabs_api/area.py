__all__ = ['Area']


class Area:
    def __init__(
                self,
                etabs=None,
                ):
        self.etabs = etabs
        self.SapModel = etabs.SapModel

    def export_freecad_slabs(self, slabs):
        self.etabs.set_current_unit('kN', 'mm')
        for slab in slabs:
            points = slab.points
            n = len(points)
            xs = [p.X for p in points]
            ys = [p.Y for p in points]
            zs = [p.Z for p in points]
            self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)

    def export_freecad_openings(self, openings):
        for opening in openings:
            points = opening.points
            n = len(points)
            xs = [p.X for p in points]
            ys = [p.Y for p in points]
            zs = [p.Z for p in points]
            ret = self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)
            name = ret[3]
            self.SapModel.AreaObj.SetOpening(name, True)


if __name__ == '__main__':
    import sys
    from pathlib import Path

    FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
    sys.path.append(FREECADPATH)
    import FreeCAD
    filename = Path(__file__).absolute().parent.parent / 'test' / 'etabs_api' / 'test_files' / 'freecad' / '2.FCStd'
    document= FreeCAD.openDocument(str(filename))
    slabs = document.Foundation.tape_slabs
    openings = document.Foundation.openings

    current_path = Path(__file__).parent
    sys.path.insert(0, str(current_path))
    from etabs_obj import EtabsModel
    etabs = EtabsModel(software='SAFE')
    SapModel = etabs.SapModel
    ret = etabs.area.export_freecad_slabs(slabs)
    ret = etabs.area.export_freecad_openings(openings)
    print('Wow')