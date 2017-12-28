from pyfakefs.fake_filesystem import FakeOsModule
from pyfakefs.fake_filesystem_shutil import FakeShutilModule
from pyfakefs.fake_filesystem import FakeFileOpen
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree
from contextlib import contextmanager


class FakeOsService:
    def __init__(self, filesystem):
        self.os_module = FakeOsModule(filesystem)
        self.shutil_module = FakeShutilModule(filesystem)
        self.filesystem = filesystem

    def listdir(self, path):
        return self.os_module.listdir(path)

    def isdir(self, path):
        return self.os_module.path.isdir(path)

    def isfile(self, path):
        return self.os_module.path.isfile(path)

    def copytree(self, src, dst):
        self.shutil_module.copytree(src, dst)

    def copyfile(self, src, dst):
        self.shutil_module.copyfile(src, dst)

    def exists(self, path):
        return self.os_module.path.exists(path)

    def makedirs(self, path):
        self.os_module.makedirs(path)

    def et_parse(self, path):
        file_module = FakeFileOpen(self.filesystem)
        with file_module(path) as file_object:
            contents = "".join([line for line in file_object])
        tree = ElementTree(ET.fromstring(contents))
        return tree

    def et_write(self, tree, path):
        contents = ET.tostring(tree.getroot())
        if self.os_module.path.exists(path):
            self.filesystem.RemoveObject(path)
        self.filesystem.CreateFile(path, contents=contents)

    @contextmanager
    def open(self, path, mode):
        file_module = FakeFileOpen(self.filesystem)

        def read():
            with file_module(path) as file_object:
                return "".join([line for line in file_object])

        def write(text):
            if self.exists(path):
                self.filesystem.RemoveObject(path)
            self.filesystem.CreateFile(path, contents=text)

        file_module.read = read
        file_module.write = write
        yield file_module

    def remove_file(self, path):
        self.os_module.unlink(path)

    def rmtree(self, path):
        self.shutil_module.rmtree(path)
