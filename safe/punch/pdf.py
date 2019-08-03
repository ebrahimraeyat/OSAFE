import matplotlib.pyplot as plt
import matplotlib.patches as patches
import FreeCAD


def createPdf(doc, pdfName):
    foun = doc.Foun
    fig = plt.figure()
    b = foun.Shape.BoundBox
    xMin, yMin, xMax, yMax = b.XMin, b.YMin, b.XMax, b.YMax
    xMin -= .2 * abs(xMin)
    yMin -= .2 * abs(yMin)
    xMax += .2 * abs(xMax)
    yMax += .2 * abs(yMax)
    ax1 = fig.add_subplot(111, aspect='equal')
    ax1.set_ylim(yMin, yMax)
    ax1.set_xlim(xMin, xMax)
    plt.axis('off')
    edges = []
    for e in foun.Shape.Edges:
        if e.BoundBox.ZLength == 0 and e.Vertexes[0].Z == 0:
            v1, v2 = e.Vertexes
            xy = [[v1.X, v1.Y], [v2.X, v2.Y]]
            p = patches.Polygon(xy, edgecolor='black', linewidth=.5)
            ax1.add_patch(p)

    text_ratio = f''
    for o in doc.Objects:
        if 'Punch' in o.Name:
            color = 'green'
            if float(o.Ratio) > 1:
                color = 'red'
            for f in o.faces:
                if f.ViewObject.isVisible():
                    xy = []
                    for v in f.Shape.Vertexes:
                        if v.Z == 0:
                            xy.append([v.X, v.Y])
                    p = patches.Polygon(xy, edgecolor='black', linewidth=.3)
                    ax1.add_patch(p)
            xy = []
            # for e in o.Shape.Edges:
            #     if e.BoundBox.ZLength == 0 and e.Vertexes[0].Z == 0:
            #         for v in e.Vertexes:
            #             xy.append([v.X, v.Y])
            # p = patches.Polygon(xy, facecolor='white', edgecolor=color, linewidth=.5)
            # ax1.add_patch(p)
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
            if o.Location in ('Corner2', 'Edge2', 'Corner3'):
                ha = 'left'
            if o.Location in ('Corner3', 'Edge3', 'Corner4'):
                va = 'bottom'
            ax1.annotate(f'{o.Location}\n{o.Ratio}', (c.x, c.y), color=color, fontsize=4, ha=ha, va=va, rotation=0, annotation_clip=False)

    FreeCAD.Console.PrintMessage("Saving pdf file...")
    fig.savefig(pdfName, orientation='portrait', papertype='letter', bbox_inches='tight')
    FreeCAD.Console.PrintMessage("Pdf file saved as: " + pdfName)
    plt.close()
