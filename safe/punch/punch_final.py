
import Part
from PySide.QtCore import QT_TRANSLATE_NOOP


class _Punch:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        property_list = obj.PropertiesList
        obj.addProperty("App::PropertyLength", "d", "Punch", QT_TRANSLATE_NOOP("App::Property", "The effective thickness of foundation")).d = 60
        # obj.addProperty("App::PropertyLength", "_d", "Default", QT_TRANSLATE_NOOP("App::Property", "The effective thickness of foundation"))
        obj.addProperty("App::PropertyEnumeration", "Location", "Punch", QT_TRANSLATE_NOOP("App::Property", "location of column"))
        obj.Location = ['Corner1', 'Corner2', 'Corner3', 'Corner4', 'Edge1', 'Edge2', 'Edge3', 'Edge4', 'Interier']
        # obj.addProperty("App::PropertyEnumeration", "LocNumber", "Punch", "Location's number of column").LocNumber = ['Corner1', 'Corner2', 'Corner3', 'Corner4']
        obj.addProperty("App::PropertyLinkList", "faces", "Punch", QT_TRANSLATE_NOOP("App::Property", "location of column"))
        obj.addProperty("App::PropertyLink", "Column", "Punch", "")
        obj.addProperty("App::PropertyInteger", "ColumnNumber")
        # obj.addProperty("Part::PropertyPartShape", "Shape", "Punch", "")
        # obj.addProperty("App::PropertyFile", "file", "Punch", "")
        # obj.addProperty("App::PropertyForce", "force", "Punch", "").force = 500
        obj.addProperty("App::PropertyLength", "primeter", "Punch", QT_TRANSLATE_NOOP("App::Property", "The area of punch")).primeter = 100
        obj.addProperty("App::PropertyInteger", "fc", "Punch", "").fc = 30
        obj.addProperty("App::PropertyLength", "bx", "Punch", "", 1, True).bx = 400
        obj.addProperty("App::PropertyLength", "by", "Punch", "", 0, True)

    def onChanged(self, fp, prop):
        # FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        # if prop == "Location":
        #     if fp.Location == 'Corner':
        #         fp.LocNumber = ['Corner1', 'Corner2', 'Corner3', 'Corner4']

        #     elif fp.Location == 'Edge':
        #         fp.LocNumber = ['Edge1', 'Edge2', 'Edge3', 'Edge4']

        #     else:
        #         fp.LocNumber = []
        #     return
        return
        # fp.Shape = Part.makeBox(fp.primeter, fp.primeter, fp.d)

    def execute(self, obj):
        # import Draft
        # downgrade = Draft.Downgrade(fp)
        #        obj.area = obj.Area
        #        faces = downgrade[0]
        # return True
        # import Part
        # obj.Shape = Part.makeBox(obj.primeter, obj.primeter, obj.d)
        return


class _ViewProviderPunch:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        #
        obj.Proxy = self

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        return

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

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
        return """
            /* XPM */
            static const char * ViewProviderBox_xpm[] = {
            "16 16 6 1",
            "   c None",
            ".  c #141010",
            "+  c #615BD2",
            "@  c #C39D55",
            "#  c #000000",
            "$  c #57C355",
            "        ........",
            "   ......++..+..",
            "   .@@@@.++..++.",
            "   .@@@@.++..++.",
            "   .@@  .++++++.",
            "  ..@@  .++..++.",
            "###@@@@ .++..++.",
            "##$.@@$#.++++++.",
            "#$#$.$$$........",
            "#$$#######      ",
            "#$$#$$$$$#      ",
            "#$$#$$$$$#      ",
            "#$$#$$$$$#      ",
            " #$#$$$$$#      ",
            "  ##$$$$$#      ",
            "   #######      "};
            """

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


obj1, obj2 = Gui.Selection.getSelection()
FreeCAD.newDocument()
outer = obj1.Shape.cut(obj2.Shape)
inner = obj1.Shape.common(obj2.Shape)
faces_outer = outer.Faces
faces_inner = inner.Faces
intersection_faces = []
for fo in faces_outer:
    for fi in faces_inner:
        if -0.01 < fo.Area - fi.Area < 0.01:
            if len(fo.Vertexes) == len(fi.Vertexes):
                no_same_V = 0
                for vo in fo.Vertexes:
                    for vi in fi.Vertexes:
                        if -.01 < vo.X - vi.X < .01 and -.01 < vo.Y - vi.Y < .01 and -.01 < vo.Z - vi.Z < .01:
                            no_same_V = no_same_V + 1
                    if no_same_V == len(fo.Vertexes):
                        intersection_faces.append(fo)

p = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Punch")
_Punch(p)
# shell = Part.makeShell(intersection_faces)
# p.Shape = shell
faces = []

for f in intersection_faces:
    face = FreeCAD.ActiveDocument.addObject("Part::Feature", "face")
    face.Shape = f
    # Gui.ActiveDocument.getObject(face.Name).Visibility = False
    faces.append(face)
p.faces = faces
p.by = 600
_ViewProviderPunch(p.ViewObject)
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewIsometric()
import Part
# s = Part.makeBox(p.bx, p.by, 4000)
# p.Column = s
FreeCAD.ActiveDocument.recompute()
