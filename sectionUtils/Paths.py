
import FreeCAD
import FreeCADGui
import os


def modulePath():
    """returns the current Plot module path."""
    path1 = FreeCAD.ConfigGet("AppHomePath") + "Mod/Section"
    path2 = FreeCAD.ConfigGet("UserAppData") + "Mod/Section"
    if os.path.exists(path2):
        return path2
    else:
        return path1


def iconsPath():
    """returns the current Section module icons path."""
    path = modulePath() + "/resources/icons"
    return path


def translationsPath():
    """returns the current Section module translations path."""
    path = modulePath() + "/resources/translations"
    return path
