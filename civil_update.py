from pathlib import Path
import os
import FreeCAD as App

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


def update():
	if (QMessageBox.question(None, "update", "update to latest version?!",
							 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.No):
		return
	if not internet():
		msg = "You are not connected to the Internet, please check your internet connection."
		QMessageBox.warning(None, 'update', str(msg))
		return

	civil_path = Path(__file__).parent.absolute()
	user_data_dir = App.getUserAppDataDir()
	if not user_data_dir in str(civil_path):
		mod_path = Path.joinpath(Path(user_data_dir), 'Mod')
		if not mod_path.exists():
			os.mkdir(mod_path)
		civil_path = Path.joinpath(mod_path, 'Civil')
	import git
	g = git.cmd.Git(civil_path)
	msg = ''
	try:
		msg = g.pull(env={'GIT_SSL_NO_VERIFY': '1'})
	except:
		QMessageBox.information(None, "update", "update takes some minutes, please be patient.")
		import shutil
		import tempfile
		default_tmp_dir = tempfile._get_default_tempdir()
		name = next(tempfile._get_candidate_names())
		punch_temp_dir = Path.joinpath(Path(default_tmp_dir), 'Civil' + name)
		os.mkdir(punch_temp_dir)
		os.chdir(punch_temp_dir)
		git.Git('.').clone("https://github.com/ebrahimraeyat/Civil.git", env={'GIT_SSL_NO_VERIFY': '1'})
		src_folder = Path.joinpath(punch_temp_dir, 'Civil')
		
		if Path.exists(civil_path):
			shutil.rmtree(civil_path)
		shutil.copytree(src_folder, civil_path)
		msg = 'update done successfully, please remove Civil folder from FreeCAD installation folder!,  then restart FreeCAD.'

	else:
		if not msg:
			msg = 'error occurred during update\nplease contact with @roknabadi'
	# msg += '\n please restart the program.'
	QMessageBox.information(None, 'update', msg)

def internet(host="8.8.8.8", port=53, timeout=3):
	import socket
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		#         print(ex.message)
		return False


if __name__ == '__main__':
	update()
