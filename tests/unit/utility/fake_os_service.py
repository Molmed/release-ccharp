from pyfakefs.fake_filesystem import FakeOsModule
from pyfakefs.fake_filesystem_shutil import FakeShutilModule


class FakeOsService:
    def __init__(self, filesystem):
        self.os_module = FakeOsModule(filesystem)
        self.shutil_module = FakeShutilModule(filesystem)

    def listdir(self, path):
        return self.os_module.listdir(path)

    def isdir(self, path):
        return self.os_module.path.isdir(path)

    def copytree(self, src, dst):
        self.shutil_module.copytree(src, dst)
