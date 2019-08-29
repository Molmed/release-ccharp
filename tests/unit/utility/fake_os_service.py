import StringIO
from pyfakefs.fake_filesystem import FakeOsModule
from pyfakefs.fake_filesystem_shutil import FakeShutilModule
from pyfakefs.fake_filesystem import FakeFileOpen
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree
from contextlib import contextmanager
from release_ccharp.utils import copytree_replace_existing


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
        copytree_replace_existing(self, src, dst)

    def copyfile(self, src, dst):
        if self.exists(dst):
            self.remove_file(dst)
        fake_open = FakeFileOpen(self.filesystem)
        with fake_open(src) as f:
            contents = ''.join([line for line in f])
        self.filesystem.create_file(dst, contents=contents)

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

        if 'r' in mode:
            with file_module(path) as file_object:
                c = "".join([line for line in file_object])
            mybuffer = StringIO.StringIO()
            mybuffer.write(c)
            mybuffer.seek(0)

        def read(n=-1):
            return mybuffer.read(n)

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
        self.filesystem.remove_object(path)
