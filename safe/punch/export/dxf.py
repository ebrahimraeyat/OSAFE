from typing import List

import FreeCAD as App
import safe.punch.punch_funcs as punch_funcs


def to_dxf(
           doc: 'App.Document',
           filename: str,
           )-> None:
    import ezdxf
    dwg = ezdxf.new()
    msp = dwg.modelspace()
    
    if not filename:
        return
    foun = doc.Foundation
    b = foun.Shape.BoundBox
    height = max(b.XLength, b.YLength)
    center = (b.Center.x, b.Center.y)
    # draw foundation
    block_foun = dwg.blocks.new(name=foun.Name)
    add_edges_to_dxf(foun.shape.Edges, {'color': 4}, block_foun)
    msp.add_blockref(foun.Name, (0 , 0))
    for o in doc.Objects:
        if hasattr(o, "Proxy") and hasattr(o.Proxy, "Type"):
            if o.Proxy.Type == "Punch":
                # draw rectangle column via hatch
                vectors = punch_funcs.rectangle_vertexes(o.center_of_load, o.bx, o.by)
                points = [(v.x, v.y) for v in vectors]
                hatch = msp.add_hatch()
                hatch.rgb = [int(i * 255) for i in o.ViewObject.ShapeColor[0:-1]]
                hatch.paths.add_polyline_path(points, is_closed=1)
                # draw punch face line
                add_edges_to_dxf(o.edges.Edges, {'color': 2}, msp)
                # add text
                t = o.text
                text = t.Text
                mtext = msp.add_mtext(f"\\S{text[0]}^ {text[1]}")
                dx, dy = t.Placement.Base.x, t.Placement.Base.y
                align = get_alignment(o)
                mtext.set_location(insert=(dx, dy, 0), attachment_point=align)
                mtext.dxf.char_height = t.ViewObject.FontSize.Value
                mtext.rgb = [int(i * 255) for i in t.ViewObject.TextColor[0:-1]]


    dwg.set_modelspace_vport(height=height, center=center)
    dwg.saveas(filename)

    FreeCAD.Console.PrintMessage("Saving dxf file...")
    FreeCAD.Console.PrintMessage("dxf file saved as: " + filename)


    # for o in doc.Objects:
    #     if not (hasattr(o, 'ViewObject') and o.ViewObject.Visibility):
    #         continue
    #     elif 'sketch' in o.Name:
    #         for g in o.Geometry:
    #             if hasattr(g, 'StartPoint'):
    #                 v1 = g.StartPoint
    #                 v2 = g.EndPoint
    #                 xy = [[v1.x, v1.y], [v2.x, v2.y]]
    #                 p = patches.Polygon(xy, edgecolor='grey', facecolor='white', linewidth=.2, linestyle='-.', closed=False)
    #                 ax1.add_patch(p)
    #             elif hasattr(g, 'Center'):
    #                 v = g.Location
    #                 x, y = v.x, v.y
    #                 r = g.Radius
    #                 p = patches.Circle([x, y], r, facecolor='white', edgecolor='black', linewidth=.3)
    #                 ax1.add_patch(p)

    #                 # XMIN = x - 2 * r
    #                 # YMAX = y + 2 * r
    #         b = o.Shape.BoundBox
    #         y_max.append(b.YMax)
    #         x_min.append(b.XMin)
    #         if 'x' in o.Name:
    #             x_max.append(b.XMax)
    #         elif 'y' in o.Name:
    #             y_min.append(b.YMin)
    #     elif 'Shape' in o.Name:
    #         v1, v2 = o.Shape.Vertexes
    #         xy = [[v1.X, v1.Y], [v2.X, v2.Y]]
    #         p = patches.Polygon(xy, edgecolor='grey', facecolor='white', linewidth=.2, linestyle='-.', closed=False)
    #         ax1.add_patch(p)

    #     elif 'Text' in o.Name:
    #         if len(o.Text) > 1:
    #             continue
    #         v = o.Placement.Base
    #         x, y = v.x, v.y
    #         ax1.annotate(o.Text[0], (x, y), color='black', fontsize=6, ha='center', va='center', rotation=0, annotation_clip=False)
    # XMIN = min(x_min) - bbbox
    # XMAX = max(x_max) + bbbox
    # YMIN = min(y_min) - bbbox
    # YMAX = max(y_max) + bbbox
    # ax1.set_ylim(YMIN, YMAX)
    # ax1.set_xlim(XMIN, XMAX)


def add_edges_to_dxf(edges, dxfattribs, block):
    for e in edges:
        if e.Length == 0:
            continue

        if len(e.Vertexes) == 2:
            if e.BoundBox.ZLength == 0:
                p1 = e.Vertexes[0]
                p2 = e.Vertexes[1]
                block.add_line((p1.X, p1.Y), (p2.X, p2.Y), dxfattribs=dxfattribs)

def get_alignment(
                  p: "FeaturePython",
                  ) -> int:
    v = "MIDDLE"
    if p.Location == "Edge1":
        v = "TOP"
    if p.Location == "Edge3":
        v = "BOTTOM"
    h = p.text.ViewObject.Justification.upper()
    alignment = f"{v}_{h}"

    alignments = {
        'TOP_LEFT': 1,
        'TOP_CENTER': 2,
        'TOP_RIGHT': 3,
        'MIDDLE_LEFT': 4,
        'MIDDLE_CENTER': 5,
        'MIDDLE_RIGHT': 6,
        'BOTTOM_LEFT': 7,
        'BOTTOM_CENTER': 8,
        'BOTTOM_RIGHT': 9,
        }
    return alignments[alignment]


if __name__ == '__main__':
    doc = FreeCAD.ActiveDocument
    to_dxf(doc, "/home/ebi/alaki/punch.dxf")
