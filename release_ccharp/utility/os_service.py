import os
from shutil import copytree
from shutil import copyfile
from xml.etree import ElementTree as ET


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

    def copyfile(self, src, dst):
        copyfile(src, dst)

    def exists(self, path):
        return os.path.exists(path)

    def makedirs(self, path):
        os.makedirs(path)

    def et_parse(self, path):
        return ET.parse(path)

    def et_write(self, tree, path):
        tree.write(path)

    def open(self, path, mode):
        return open(path, mode)

