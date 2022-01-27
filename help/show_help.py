from pathlib import Path

import FreeCADGui as Gui

def show(filename):
    try:
        import Help
    except ModuleNotFoundError:
        from PySide2.QtWidgets import QMessageBox
        if (QMessageBox.question(
                None,
                "Install Help",
                "You must install Help WB to view the manual, do you want to install it?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.No):
            return
        Gui.runCommand('Std_AddonMgr',0)
        return
    help_path = Path(__file__).parent / filename
    Help.show(str(help_path))