from pathlib import Path

import FreeCAD

import etabs_obj

def open(filename):
    # import os
    # docname = os.path.splitext(os.path.basename(filename))[0]
    # doc = FreeCAD.newDocument(docname)
    # doc.Label = docname
    insert(filename)
    # return doc


def insert(filename):
    param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
    use_etabs = param.GetBool('use_etabs', False)
    software_exe_path = param.GetString('etabs_exe_path', '')
    if (
        use_etabs and
        Path(software_exe_path).exists
        ):
        attach_to_instance = False
    else:
        attach_to_instance = True
    etabs = etabs_obj.EtabsModel(
                attach_to_instance=attach_to_instance,
                backup = False,
                model_path = Path(filename),
                software_exe_path=software_exe_path,
            )
    FreeCAD.etabs = etabs
