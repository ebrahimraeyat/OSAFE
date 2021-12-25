import sys
from pathlib import Path

from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent
serial_base, serial_window = loadUiType(str(civiltools_path / 'widgets' / 'serial.ui'))


def allowed_to_continue(
                        filename,
                        gist_url,
                        dir_name,
                        n=5,
                        ):
    sys.path.insert(0, str(civiltools_path))
    from functions import check_legal
    check = check_legal.CheckLegalUse(
                                filename,
                                gist_url,
                                dir_name,
                                n,
    )
    allow, text = check.allowed_to_continue()
    if allow and not text:
        return True, check
    else:
        if text in ('INTERNET', 'SERIAL'):
            serial_win = SerialForm()
            serial_win.serial.setText(check.serial)
            serial_win.exec_()
            return False, check
        elif text == 'REGISTERED':
            msg = "Congrajulation! You are now registered, enjoy using this features!"
            QMessageBox.information(None, 'Registered', str(msg))
            return True, check
    return False, check

def show_warning_about_number_of_use(check):
    if check.is_civiltools_registered:
        return
    elif check.is_registered:
        check.add_using_feature()
        _, no_of_use = check.get_registered_numbers()
        n = check.n - no_of_use
        msg = ''
        if n == 0:
            msg = f"You can't use this feature any more times!\n please register the software."
        elif n > 0:
            msg = f"You can use this feature {n} more times!\n then you must register the software."
        if msg:
            QMessageBox.warning(None, 'Not registered!', str(msg))


class SerialForm(serial_base, serial_window):
# class SerialForm(*loadUiType(str(civiltools_path / 'widgets' / 'serial.ui'))):
    def __init__(self, parent=None):
        super(SerialForm, self).__init__()
        self.setupUi(self)
        self.submit_button.clicked.connect(submit)


def submit():
    sys.path.insert(0, str(civiltools_path))
    from functions import check_legal
    check = check_legal.CheckLegalUse(
        'civiltools5.bin',
        'https://gist.githubusercontent.com/ebrahimraeyat/b8cbd078eb7b211e3154804a8bb77633/raw',
        'cfactor',
        )
    text = check.submit()

    if text == 'INTERNET':
        msg = 'Please connect to the internet!'
    elif text == 'SERIAL':
        msg = 'You are not registered, Please Contact author to buy the software.'
    elif text == 'REGISTERED':
        msg = "Congrajulation! You are now registered, enjoy using CivilTools."
    QMessageBox.information(None, 'Registeration', msg)