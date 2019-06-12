from PySide.QtCore import QT_TRANSLATE_NOOP


class _Punch:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        property_list = obj.PropertiesList
        obj.addProperty("App::PropertyLength", "d", "Punch", QT_TRANSLATE_NOOP("App::Property", "The effective thickness of foundation")).d = 60
        obj.addProperty("App::PropertyLength", "_d", "Default", QT_TRANSLATE_NOOP("App::Property", "The effective thickness of foundation"))
        obj.addProperty("App::PropertyEnumeration", "Location", "Punch", QT_TRANSLATE_NOOP("App::Property", "location of column")).Location = ['Corner', 'Edge', 'Interier']
        obj.addProperty("App::PropertyEnumeration", "LocNumber", "Punch", "Location's number of column").LocNumber = ['Corner1', 'Corner2', 'Corner3', 'Corner4']
        obj.addProperty("App::PropertyEnumeration", "faces", "Punch", QT_TRANSLATE_NOOP("App::Property", "location of column"), -1)
        obj.addProperty("App::PropertyLink", "Link", "Punch", "")
        obj.addProperty("App::PropertyFile", "file", "Punch", "")
        obj.addProperty("App::PropertyForce", "force", "Punch", "").force = 500
        obj.addProperty("App::PropertyLength", "primeter", "Punch", QT_TRANSLATE_NOOP("App::Property", "The area of punch")).primeter = 100

    def onChanged(self, fp, prop):
        # FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        if prop == "Location":
            if fp.Location == 'Corner':
                fp.LocNumber = ['Corner1', 'Corner2', 'Corner3', 'Corner4']

            elif fp.Location == 'Edge':
                fp.LocNumber = ['Edge1', 'Edge2', 'Edge3', 'Edge4']

            else:
                fp.LocNumber = []
            return
        # fp.Shape = Part.makeBox(fp.primeter, fp.primeter, fp.d)

    def execute(self, obj):
        # import Draft
        # downgrade = Draft.Downgrade(fp)
        #        obj.area = obj.Area
        #        faces = downgrade[0]
        # return True
        import Part
        obj.Shape = Part.makeBox(obj.primeter, obj.primeter, obj.d)


class _ViewProviderPunch:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        # obj.addProperty("App::PropertyMaterial", "material", "Punch", "")
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


def make_punch():
    FreeCAD.newDocument()
    p = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Punch")
    _Punch(p)
    _ViewProviderPunch(p.ViewObject)
    import Arch
    s = Arch.makeStructure(length=100.0, width=100.0, height=1000.0)
    p.Link = s
    FreeCAD.ActiveDocument.recompute()


make_punch()
