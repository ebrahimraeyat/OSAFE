import Sketcher
import FreeCAD
import FreeCADGui as Gui
import Part
import Draft

font_size = 500
o = 500
l = 500
r = 500
yt = font_size / 3
no_of_edge_in_on_axis = 4

# x_grid_group.addObject(x_sketch)


def create_x_grid(sketch, xcoord, text, i, YMIN, YMAX, y1, y2, y3, y4, yc):
    text = str(text)
    if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("extend_grid", True):
        g = Part.makeLine(FreeCAD.Vector(xcoord, YMIN, 0), FreeCAD.Vector(xcoord, YMAX, 0))
        Part.show(g)
    # g.ViewObject.DrawStyle = 'Dashdot'
    # x_grid_group.addObject(g0)
    g1 = sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(xcoord, y1, 0), FreeCAD.Vector(xcoord, y2, 0)))
    g2 = sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(xcoord, y2, 0), FreeCAD.Vector(xcoord, y3, 0)))
    g3 = sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(xcoord, y3, 0), FreeCAD.Vector(xcoord, y4, 0)))
    g4 = sketch.addGeometry(Part.Circle(FreeCAD.Vector(xcoord, yc, 0), FreeCAD.Vector(0, 0, 1), r), False)

    t = Draft.makeText(text, FreeCAD.Vector(xcoord, yc, 0))
    t.ViewObject.FontSize = font_size
    t.ViewObject.Justification = 'Center'

    # x_grid_group.addObject(t)
    sketch.addConstraint(Sketcher.Constraint('DistanceX', g1, 1, xcoord))
    sketch.addConstraint(Sketcher.Constraint('DistanceY', g1, 1, y1))
    sketch.addConstraint(Sketcher.Constraint('Coincident', g1, 2, g2, 1))
    sketch.addConstraint(Sketcher.Constraint('Coincident', g2, 2, g3, 1))
    sketch.addConstraint(Sketcher.Constraint('Vertical', g1))
    sketch.addConstraint(Sketcher.Constraint('Vertical', g3))
    sketch.addConstraint(Sketcher.Constraint('Radius', g4, r))
    sketch.addConstraint(Sketcher.Constraint('PointOnObject', g3, 2, g4))
    sketch.addConstraint(Sketcher.Constraint('Perpendicular', g4, g3))
    const_num = sketch.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, g4, 3, xcoord))
    sketch.renameConstraint(const_num, f'x_{text}')
    sketch.toggleDriving(const_num)
    const_num = sketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1, g4, 3, yc))
    sketch.renameConstraint(const_num, f'y_{text}')
    sketch.toggleDriving(const_num)
    t.setExpression('Placement.Base.x', f'{sketch.Name}.Constraints.x_{text}')
    t.setExpression('Placement.Base.y', f'{sketch.Name}.Constraints.y_{text}')

    if not i == no_of_edge_in_on_axis - 1:
        sketch.addConstraint(Sketcher.Constraint('DistanceY', g4, 3, g4 - no_of_edge_in_on_axis, 3, 0))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', g1, 2, g1 - no_of_edge_in_on_axis, 2, 0))


def create_y_grid(sketch, ycoord, text, i, XMIN, XMAX, x1, x2, x3, x4, xc):
    text = str(text)
    if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("extend_grid", True):
        g = Part.makeLine(FreeCAD.Vector(XMIN, ycoord, 0), FreeCAD.Vector(XMAX, ycoord, 0))
    # # g.DrawStyle = "Dashdot"
        Part.show(g)
    # x_grid_group.addObject(g0)
    g1 = sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, ycoord, 0), FreeCAD.Vector(x2, ycoord, 0)))
    g2 = sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, ycoord, 0), FreeCAD.Vector(x3, ycoord, 0)))
    g3 = sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x3, ycoord, 0), FreeCAD.Vector(x4, ycoord, 0)))
    g4 = sketch.addGeometry(Part.Circle(FreeCAD.Vector(xc, ycoord, 0), FreeCAD.Vector(0, 0, 1), r), False)

    t = Draft.makeText(text, FreeCAD.Vector(xc, ycoord, 0))
    t.ViewObject.FontSize = font_size
    t.ViewObject.Justification = 'Center'

    # x_grid_group.addObject(t)
    sketch.addConstraint(Sketcher.Constraint('DistanceY', g1, 1, ycoord))
    sketch.addConstraint(Sketcher.Constraint('DistanceX', g1, 1, x1))
    sketch.addConstraint(Sketcher.Constraint('Coincident', g1, 2, g2, 1))
    sketch.addConstraint(Sketcher.Constraint('Coincident', g2, 2, g3, 1))
    sketch.addConstraint(Sketcher.Constraint('Horizontal', g1))
    sketch.addConstraint(Sketcher.Constraint('Horizontal', g3))
    sketch.addConstraint(Sketcher.Constraint('Radius', g4, r))
    sketch.addConstraint(Sketcher.Constraint('PointOnObject', g3, 2, g4))
    sketch.addConstraint(Sketcher.Constraint('Perpendicular', g4, g3))
    const_num = sketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1, g4, 3, ycoord))
    sketch.renameConstraint(const_num, f'y_{text}')
    sketch.toggleDriving(const_num)
    const_num = sketch.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, g4, 3, xc))
    sketch.renameConstraint(const_num, f'x_{text}')
    sketch.toggleDriving(const_num)
    t.setExpression('Placement.Base.x', f'{sketch.Name}.Constraints.x_{text}')
    t.setExpression('Placement.Base.y', f'{sketch.Name}.Constraints.y_{text}')

    if not i == no_of_edge_in_on_axis - 1:
        sketch.addConstraint(Sketcher.Constraint('DistanceX', g4, 3, g4 - no_of_edge_in_on_axis, 3, 0))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', g1, 2, g1 - no_of_edge_in_on_axis, 2, 0))


def create_grids(grids, boundBox, direction='x'):
    XMIN = boundBox.XMin
    XMAX = boundBox.XMax
    YMIN = boundBox.YMin
    YMAX = boundBox.YMax

    coords = list(grids.values())
    texts = list(grids.keys())
    doc = FreeCAD.ActiveDocument
    if direction == 'x':
        y1 = YMAX + o
        y2 = y1 + l
        y3 = y2 + l
        y4 = y3 + l
        yc = y4 + r
        sketch = doc.addObject('Sketcher::SketchObject', 'x_sketch')
        i = no_of_edge_in_on_axis - 1
        for coord, text in zip(coords, texts):
            create_x_grid(sketch, coord, text, i, YMIN, YMAX, y1, y2, y3, y4, yc)
            i += no_of_edge_in_on_axis
    elif direction == 'y':
        x1 = XMIN - o
        x2 = x1 - l
        x3 = x2 - l
        x4 = x3 - l
        xc = x4 - r
        sketch = doc.addObject('Sketcher::SketchObject', 'y_sketch')
        i = no_of_edge_in_on_axis - 1
        for coord, text in zip(coords, texts):
            create_y_grid(sketch, coord, text, i, XMIN, XMAX, x1, x2, x3, x4, xc)
            i += no_of_edge_in_on_axis

    sketch.ViewObject.LineWidth = 1.
    sketch.ViewObject.PointSize = 1.

    doc.recompute()


if __name__ == '__main__':
    doc = FreeCAD.newDocument("grid")
    # x_grid_group = doc.addObject("App::DocumentObjectGroup", "x_grid")

    create_grids([0, 500, 1000, 1500], ['A', 'B', 'C', 'D'], x_sketch)
