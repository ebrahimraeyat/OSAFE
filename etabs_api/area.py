from typing import Union


if __name__ == '__main__':
    import sys
    FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
    sys.path.append(FREECADPATH)
try:
    import FreeCAD
    import Part
except:
    pass

__all__ = ['Area']


class Area:
    def __init__(
                self,
                etabs=None,
                ):
        self.etabs = etabs
        self.SapModel = etabs.SapModel

    def export_freecad_slabs(self, doc : 'App.Document' = None):
        self.etabs.set_current_unit('kN', 'mm')
        if doc is None:
            doc = FreeCAD.ActiveDocument
        foun = doc.Foundation
        if foun.foundation_type == 'Strip':
            slabs = foun.tape_slabs
            for slab in slabs:
                points = slab.points
                self.create_area_by_coord(points)
        elif foun.foundation_type == 'Mat':
            edges = foun.plane_without_openings.Edges
            points = self.get_sort_points(edges)
            self.create_area_by_coord(points)

    def get_sort_points(self, edges):
        points = []
        edges = Part.__sortEdges__(edges)
        for e in edges:
            v = e.firstVertex()
            points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
        return points

    def create_area_by_coord(self,
            points : 'Base.Vector',
            prop_name : Union[str, bool] = None,
            ):
        n = len(points)
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        zs = [p.z for p in points]
        if prop_name is None:
            self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)
        else:
            self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs, PropName=prop_name)

    def export_freecad_openings(self, doc : 'App.Document' = None):
        self.etabs.set_current_unit('kN', 'mm')
        if doc is None:
            doc = FreeCAD.ActiveDocument
        openings = doc.Foundation.openings
        for opening in openings:
            points = opening.points
            n = len(points)
            xs = [p.x for p in points]
            ys = [p.y for p in points]
            zs = [p.z for p in points]
            ret = self.SapModel.AreaObj.AddByCoord(n, xs, ys, zs)
            name = ret[3]
            self.SapModel.AreaObj.SetOpening(name, True)

    def export_freecad_strips(self, doc : 'App.Document' = None):
        self.etabs.set_current_unit('kN', 'mm')
        if doc is None:
            doc = FreeCAD.ActiveDocument
        foun = doc.Foundation
        data = []
        if foun.foundation_type == 'Strip':
            slabs = foun.tape_slabs
            i = j = 0
            for slab in slabs:
                p1 = slab.start_point
                p2 = slab.end_point
                p = self.SapModel.PointObj.AddCartesian(p1.x, p1.y, p1.z)
                p1_name = p[0]
                p = self.SapModel.PointObj.AddCartesian(p2.x, p2.y, p2.z)
                p2_name = p[0]
                swl = ewl = slab.width.Value / 2 + slab.offset
                swr = ewr = slab.width.Value / 2 - slab.offset
                dx = abs(p1.x - p2.x)
                dy = abs(p1.y - p2.y)
                if dx > dy:
                    layer = 'A'
                    i += 1
                    name = f'CS{layer}{i}'
                else:
                    layer = 'B'
                    j += 1
                    name = f'CS{layer}{j}'
                data.extend((
                    name,
                    '1',
                    f'{p1_name}',
                    f'{p2_name}',
                    f'{swl}',
                    f'{swr}',
                    f'{ewl}',
                    f'{ewr}',
                    'NO',
                    f'{layer}',
                    ))
        table_key = 'Strip Object Connectivity'
        fields = ['Name', 'NumSegs', 'StartPoint', 'EndPoint', 'WStartLeft',
            'WStartRight', 'WEndLeft', 'WEndRight', 'AutoWiden', 'Layer']
        if self.etabs.software == 'ETABS':
            fields.insert(1, 'Story')
        assert len(fields) == len(data) / len(slabs)
        self.etabs.database.apply_data(table_key, data, fields)

    def export_freecad_stiff_elements(self, doc : 'App.Document' = None):
        self.etabs.set_current_unit('kN', 'mm')
        self.SapModel.PropMaterial.SetMaterial('CONCRETE_ZERO', 2)
        self.SapModel.PropMaterial.SetWeightAndMass('CONCRETE_ZERO', 1, 0)
        self.SapModel.PropMaterial.SetWeightAndMass('CONCRETE_ZERO', 2, 0)
        self.SapModel.PropArea.SetSlab('COL_STIFF', 2, 2, 'CONCRETE_ZERO', 1500)

        if doc is None:
            doc = FreeCAD.ActiveDocument
        for o in doc.Objects:
            if (hasattr(o, "Proxy") and 
                hasattr(o.Proxy, "Type") and 
                o.Proxy.Type == "Punch"
                ):
                points = self.get_sort_points(o.rect.Edges)
                self.create_area_by_coord(points, prop_name='COL_STIFF')
 

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
    ret = etabs.area.export_freecad_stiff_elements(document)
    ret = etabs.area.export_freecad_openings(openings)
    print('Wow')