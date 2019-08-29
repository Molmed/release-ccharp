from pyfakefs.fake_filesystem import FakeOsModule
from pyfakefs.fake_filesystem import FakeFileOpen


class FakeWindowsCommands:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.os_module = FakeOsModule(filesystem)

    def build_solution(self, path):
        pass

    def create_shortcut(self, save_path, target_path):
        if not self.os_module.path.exists(save_path):
            self.filesystem.create_file(save_path, contents=target_path)

    def extract_shortcut_target(self, shortcut_path):
        file_module = FakeFileOpen(self.filesystem)
        with file_module(shortcut_path) as f:
            contents = "".join([line for line in f])
        return contents

