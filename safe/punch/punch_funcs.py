import FreeCAD

def remove_obj(name: str) -> None:
    o = FreeCAD.ActiveDocument.getObject(name)
    if hasattr(o, "Base") and o.Base:
        remove_obj(o.Base.Name)
    if hasattr(o, "Tool") and o.Tool:
    	remove_obj(o.Tool.Name)
    if hasattr(o, "Shapes") and o.Shapes:
    	for sh in o.Shapes:
    		remove_obj(sh.Name)
    FreeCAD.ActiveDocument.removeObject(name)