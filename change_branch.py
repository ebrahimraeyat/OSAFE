from pathlib import Path

from PySide2.QtWidgets import  QMessageBox
import FreeCADGui as Gui
import git

civil_path = Path(__file__).parent


class Form:

    def __init__(self,
            git_url : str = "https://github.com/ebrahimraeyat/Civil.git"):
        self.git_url = git_url
        self.form = Gui.PySideUic.loadUi(str(civil_path / 'Resources' / 'ui' / 'change_branch.ui'))
    #     self.fill_branches()

    # def fill_branches(self):
    #     repo = git.Repo(civil_path)
    #     branch_names = [branch.name for branch in repo.branches]
    #     if branch_names:
    #         self.form.branch_list.addItems(branch_names)


    def accept(self):
        g = git.cmd.Git(civil_path)
        branch = self.form.branch_list.currentItem().text()
        if not branch:
            return
        succeed = self.checkout(g, branch)
        if not succeed:
            if not internet():
                msg = "You are not connected to the Internet, please check your internet connection."
                QMessageBox.warning(None, 'update', str(msg))
                return
            QMessageBox.information(
                None,
                "Download",
                "Download takes some minutes, please be patient.",
                )
            g.execut(f'git clone --branch {branch} --depth 1 {self.git_url}')
            self.checkout(g, branch)
        Gui.Control.closeDialog()

    def checkout(self, g, branch):
        try:
            g.execute(f'git checkout {branch}')
            msg = f'You have successfully move to {branch}'
            QMessageBox.information(None, 'Change Branch', str(msg))
            return True
        except:
            return False


def internet(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        #         print(ex.message)
        return False