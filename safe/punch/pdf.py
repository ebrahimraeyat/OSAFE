import matplotlib.pyplot as plt
import matplotlib.patches as patches
import FreeCAD


def createPdf(doc, pdfName):
    if not pdfName:
        return
    foun = doc.Foun
    fig = plt.figure()
    b = foun.Shape.BoundBox
    XMIN, YMIN, XMAX, YMAX = b.XMin, b.YMin, b.XMax, b.YMax
    XMIN -= .2 * abs(XMIN)
    YMIN -= .2 * abs(YMIN)
    XMAX += .2 * abs(XMAX)
    YMAX += .2 * abs(YMAX)
    x_max = [XMAX]
    x_min = [XMIN]
    y_max = [YMAX]
    y_min = [YMIN]
    bbbox = 500
    ax1 = fig.add_subplot(111, aspect='equal')
    plt.axis('off')

    for e in foun.Shape.Edges:
        if not len(e.Vertexes) == 2:
            continue
        if e.BoundBox.ZLength == 0 and e.Vertexes[0].Z == 0:
            v1, v2 = e.Vertexes
            xy = [[v1.X, v1.Y], [v2.X, v2.Y]]
            p = patches.Polygon(xy, edgecolor='black', linewidth=.5, closed=False)
            ax1.add_patch(p)

    text_ratio = f''
    for o in doc.Objects:
        if not (hasattr(o, 'ViewObject') and o.ViewObject.Visibility):
            continue
        if 'Punch' in o.Name:
            color = o.ViewObject.ShapeColor[:-1]
            for f in o.faces:
                if f.ViewObject.isVisible():
                    xy = []
                    for v in f.Shape.Vertexes:
                        if v.Z == 0:
                            xy.append([v.X, v.Y])
                    p = patches.Polygon(xy, edgecolor='black', linewidth=.4, linestyle='--', closed=False)
                    ax1.add_patch(p)
            xy = []

            for f in o.Shape.Faces:
                b = f.BoundBox
                if b.ZLength == 0 and b.ZMax == 0:
                    xmin, ymin = b.XMin, b.YMin
                    p = patches.Rectangle((xmin, ymin), o.bx, o.by, facecolor=color, edgecolor='black', linewidth=.3)
                    ax1.add_patch(p)

            text_ratio += f'{o.number}:{o.Location}, ratio = {o.Ratio}\n'
            c = o.text.Placement.Base
            ha = 'right'
            va = 'center'
            if o.Location in ('Corner2', 'Edge2', 'Corner3', 'Interier'):
                ha = 'left'
            if o.Location in ('Corner3', 'Edge3', 'Corner4', 'Interier'):
                va = 'bottom'
            ax1.annotate(f'{o.Location}\n{o.Ratio}', (c.x, c.y), color=color, fontsize=4, ha=ha, va=va, rotation=0, annotation_clip=False)

        elif 'sketch' in o.Name:
            for g in o.Geometry:
                if hasattr(g, 'StartPoint'):
                    v1 = g.StartPoint
                    v2 = g.EndPoint
                    xy = [[v1.x, v1.y], [v2.x, v2.y]]
                    p = patches.Polygon(xy, edgecolor='grey', facecolor='white', linewidth=.2, linestyle='-.', closed=False)
                    ax1.add_patch(p)
                elif hasattr(g, 'Center'):
                    v = g.Location
                    x, y = v.x, v.y
                    r = g.Radius
                    p = patches.Circle([x, y], r, facecolor='white', edgecolor='black', linewidth=.3)
                    ax1.add_patch(p)

                    # XMIN = x - 2 * r
                    # YMAX = y + 2 * r
            b = o.Shape.BoundBox
            y_max.append(b.YMax)
            x_min.append(b.XMin)
            if 'x' in o.Name:
                x_max.append(b.XMax)
            elif 'y' in o.Name:
                y_min.append(b.YMin)
        elif 'Shape' in o.Name:
            v1, v2 = o.Shape.Vertexes
            xy = [[v1.X, v1.Y], [v2.X, v2.Y]]
            p = patches.Polygon(xy, edgecolor='grey', facecolor='white', linewidth=.2, linestyle='-.', closed=False)
            ax1.add_patch(p)

        elif 'Text' in o.Name:
            if len(o.Text) > 1:
                continue
            v = o.Placement.Base
            x, y = v.x, v.y
            ax1.annotate(o.Text[0], (x, y), color='black', fontsize=6, ha='center', va='center', rotation=0, annotation_clip=False)
    XMIN = min(x_min) - bbbox
    XMAX = max(x_max) + bbbox
    YMIN = min(y_min) - bbbox
    YMAX = max(y_max) + bbbox
    ax1.set_ylim(YMIN, YMAX)
    ax1.set_xlim(XMIN, XMAX)

    FreeCAD.Console.PrintMessage("Saving pdf file...")
    fig.savefig(pdfName, orientation='portrait', papertype='a4', bbox_inches='tight', dpi=600)
    FreeCAD.Console.PrintMessage("Pdf file saved as: " + pdfName)
    plt.close()


# doc = FreeCAD.ActiveDocument
# createPdf(doc, '/home/ebi/punch.pdf')
