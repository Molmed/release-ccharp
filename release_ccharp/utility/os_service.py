import os
from shutil import copytree


class OsService():
    """
    Encapsulates os calls in order to make possible to mock them in tests
    """
    def listdir(self, path):
        return  os.listdir(path)

    def isdir(self, path):
        return os.path.isdir(path)

    def copytree(self, src, dst):
        copytree(src, dst)
