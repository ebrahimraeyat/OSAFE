import math
import Part
import FreeCAD
import FreeCADGui


def make_rectangle_slab(p1, p2, width=1, height=1):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Slab")
    RectangleSlab(obj)
    obj.start_point = p1
    obj.end_point = p2
    obj.width = width
    obj.height = height
    if FreeCAD.GuiUp:
        _ViewProviderStrip(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class RectangleSlab:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "tape_slab"
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.addProperty("App::PropertyVector", "start_point", "slab", "")
        obj.addProperty("App::PropertyVector", "end_point", "slab", "")
        obj.addProperty("App::PropertyLength", "width", "slab", "")
        obj.addProperty("App::PropertyLength", "height", "slab", "")
        obj.addProperty("App::PropertyAngle", "angle", "slab", "", 1, True)

    def onChanged(self, obj, prop):
        return

    def execute(self, obj):
        v = obj.end_point - obj.start_point
        obj.angle = math.atan2(v.y, v.x)
        self.create_width(obj)

    def create_width(self, obj):
        points = []
        xs = obj.start_point.x
        ys = obj.start_point.y
        xe = obj.end_point.x
        ye = obj.end_point.y
        w = obj.width.Value / 2
        teta = obj.angle
        # FreeCAD.Console.PrintMessage(f"teta = {teta}")
        _sin = math.sin(teta)
        _cos = math.cos(teta)
        x = xs - w * _sin
        y = ys + w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xs + w * _sin
        y = ys - w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xe + w * _sin
        y = ye - w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        x = xe - w * _sin
        y = ye + w * _cos
        points.append(FreeCAD.Vector(x, y, 0))
        points.append(points[0])
        face = Part.Face(Part.makePolygon(points))
        obj.Shape = face.extrude(FreeCAD.Vector(0, 0, -obj.height.Value))

class _ViewProviderStrip:
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyBool", "show_width", "display", "")

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        return

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def execute(self, obj):
        print("view execute!")

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Flat Line"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optional.
        '''
        return mode

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        # FreeCAD.Console.PrintMessage("Change View property: " + str(prop) + "\n")
        return

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return None

    def __getstate__(self):
        ''' When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.
        '''
        return None

    def __setstate__(self, state):
        ''' When restoring the pickled object from document we have the chance to set some
        internals here. Since no data were pickled nothing needs to be done here.
        '''
        return None


if __name__ == "__main__":
    make_rectangle_slab(
            p1=FreeCAD.Vector(0, 0, 0),
            p2=FreeCAD.Vector(1, 1, 0),
            width = .5,
            height = 2,
               )
