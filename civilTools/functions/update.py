import os
import sys
from pathlib import Path

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))


class GitUpdate:

    def __init__(self,
                branch='v6',
                git_url="https://github.com/ebrahimraeyat/civilTools.git",
                ):
        self.git_url = git_url
        self.branch = branch

    def git_update(self):       
        import git
        from git import Repo, Git
        g = git.cmd.Git(str(civiltools_path))
        msg = ''
        try:
            g.execute('git submodule update --init --recursive')
            msg = g.execute(f'git pull --recurse-submodules origin {self.branch}')
            if not 'already' in msg.lower():
                msg = 'update done successfully.'
        except:
            import shutil
            import tempfile
            default_tmp_dir = tempfile._get_default_tempdir()
            name = next(tempfile._get_candidate_names())
            civiltools_temp = Path(default_tmp_dir) /  'civiltools'
            if not civiltools_temp.exists():
                civiltools_temp.mkdir()
            civiltools_temp_dir = Path(default_tmp_dir) /  'civiltools' / name
            civiltools_temp_dir.mkdir()
            os.chdir(str(civiltools_temp_dir))
            g.execute(f'git clone --branch {self.branch} --depth 1 --recurse-submodules {self.git_url}')
            shutil.rmtree(str(civiltools_path), onerror=onerror)
            src_folder = civiltools_temp_dir / 'civilTools'
            shutil.copytree(str(src_folder), str(civiltools_path))
            os.chdir(str(civiltools_path))
            msg = 'update done successfully.'
        else:
            if not msg:
                msg = 'error occured during update\nplease contact with @roknabadi\
                    Email: ebe79442114@yahoo.com, ebe79442114@gmail.com'
        g = Git(civiltools_path)
        g.execute(['git', 'checkout', self.branch])
        return msg

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        print('another error')
        raise


def internet(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        #         print(ex.message)
        return False
